import pymongo
import pymongo.results
from ...interfaceCarritoDAO import InterfaceCarritoDAO
from ....dto.carritoDTO import CarritoDTO, ArticuloCestaDTO
from bson import ObjectId

PDAO = "\033[95mDAO\033[0m:\t "
PDAO_ERROR = "\033[96mDAO\033[0m|\033[91mERROR\033[0m:\t "

# Esta clase implementa los métodos que se usaran en las llamadas del Model.
# En concreto, esta es la clase destinada para lo relacionado con la colección del Carrito en MongoDB.
class mongodbCarritoDAO(InterfaceCarritoDAO):

    # En el constructor de la clase, se recibe la colección de MongoDB que se va a usar para interactuar con la base de datos.
    def __init__(self, collection):
        self.collection = collection
    
    def get_all_articulos(self, usuario) -> dict:
        articulos = CarritoDTO()
        subtotal = 0.0
        try:
            # Buscamos el documento del carrito del usuario
            carrito = self.collection.find_one({"usuario": usuario})

            if carrito and "articulos" in carrito:
                for doc in carrito["articulos"]:
                    articulo_cesta_dto = ArticuloCestaDTO()
                    articulo_cesta_dto.set_id(doc.get("id"))
                    articulo_cesta_dto.set_precio(str(doc.get("precio")))
                    articulo_cesta_dto.set_nombre(str(doc.get("nombre")))
                    articulo_cesta_dto.set_descripcion(str(doc.get("descripcion")))
                    articulo_cesta_dto.set_artista(str(doc.get("artista")))
                    articulo_cesta_dto.set_cantidad(str(doc.get("cantidad")))
                    articulo_cesta_dto.set_imagen(str(doc.get("imagen")))
                    subtotal += float(doc.get("precio")) * int(doc.get("cantidad"))
                    articulos.subtotal = subtotal
                    articulos.insertArticuloCesta(articulo_cesta_dto)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al recuperar los artículos: {e}")

        return articulos.to_dict()


    def upsert_articulo_en_carrito(self, usuario, articulo: ArticuloCestaDTO) -> bool:
        try:
            articulo_dict = articulo.articulocestadto_to_dict()
            filtro_usuario = {"usuario": usuario}

            existing_carrito = self.collection.find_one(filtro_usuario)

            if existing_carrito:
                return self.agregar_articulo_a_carrito(usuario, articulo_dict)
            else:
                return self.crear_carrito(usuario, articulo_dict)

        except Exception as e:
            print(f"{PDAO_ERROR}Error al insertar/actualizar artículo en carrito: {e}")
            return False
        

    def articulo_existe_en_carrito(self, carrito: dict, articulo_id: str) -> bool:
        return any(art["id"] == articulo_id for art in carrito.get("articulos", []))


    def agregar_articulo_a_carrito(self, usuario, articulo_dict) -> bool:
        result = self.collection.update_one(
            {"usuario": usuario},
            {
                "$push": {"articulos": articulo_dict},
                "$inc": {"subtotal": float(articulo_dict.get("precio", 0))}
            }
        )
        return result.modified_count == 1


    def crear_carrito(self, usuario, articulo_dict) -> bool:
        carrito_dict = {
            "usuario": usuario,
            "articulos": [articulo_dict],
            "subtotal": float(articulo_dict.get("precio", 0))
        }
        result = self.collection.insert_one(carrito_dict)
        return result.acknowledged
    
    def vaciar_carrito(self, usuario: str) -> bool:
        try:
            # Realizamos una actualización en la base de datos para eliminar todos los artículos
            result = self.collection.update_one(
                {"usuario": usuario},
                {
                    "$set": {"articulos": [], "subtotal": 0}  # Vaciar los artículos y poner subtotal en 0
                }
            )

            # Retornamos True si se modificó el documento (carrito) correctamente
            return result.modified_count == 1
        except Exception as e:
            print(f"{PDAO_ERROR}Error al vaciar el carrito: {e}")
            return False


    def deleteArticuloDelCarrito(self, usuario, id_articulo) -> bool:
        try:
            articulo = self.collection.find_one(
                {"usuario": usuario, "articulos.id": id_articulo},
                {"articulos.$": 1}
            )
            if not articulo or not articulo.get("articulos"):
                return False

            art = articulo["articulos"][0]
            precio_total = float(art.get("precio", 0)) * float(art.get("cantidad", 1))

            result = self.collection.update_one(
                {"usuario": usuario},
                {
                    "$pull": {"articulos": {"id": id_articulo}},
                    "$inc": {"subtotal": -precio_total}
                }
            )
            return result.modified_count == 1
        
        except Exception as e:
            print(f"{PDAO_ERROR}Error al eliminar artículo del carrito: {e}")
            return False



        
        

    