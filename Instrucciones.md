# 🧩 Implementación de endpoints con MVC + DAO + Factory + MongoDB

## ✅ Paso 1: Crear el DTO 
Esta clase se encarga de representar una entidad de forma simple. No tiene lógica, solo guarda y mueve datos entre capas del sistema (controlador, modelo, DAO...).

Define los métodos:
- Getters y setters para cada atributo.
- Métodos auxiliares como `to_dict()` si quieres convertir el objeto a JSON.

## ✅ Paso 2: Crear el interfaceDAO
Esta clase se encarga de definir los métodos que debe tener cualquier clase DAO que gestione una entidad concreta, sin importar la tecnología usada.
Define los métodos:
- `get_all()`
- (Opcionalmente) `get_by_id()`, `insert()`, `update()`, `delete()`

## ✅ Paso 3: Crear el DAO
Esta clase se encarga de implementar los métodos definidos en la interfaz DAO, conectándose a una base de datos real para leer o modificar información.
Define las funciones concretas para operar sobre la base de datos:
- `find()`, `insert_one()`, `update_one()`, `delete_one()`...

## ✅ Paso 4: Modificar mongodbConnector
Esta clase se encarga de centralizar la conexión con MongoDB. Asegura que solo haya una instancia activa, reutilizable y segura.
Define los métodos:
- `get_db()` → devuelve la base de datos.  
- `get_collection()` → devuelve la colección deseada.

## ✅ Paso 5: Modificar interfaceDAOFactory
Esta clase se encarga de definir los métodos que debe implementar cualquier fábrica de DAOs. Permite crear DAOs sin que el modelo sepa de qué tipo son (Mongo, Firebase...).
Define los métodos:
- `get_dao()`  para cada una de las entidades de las que se disponga

## ✅ Paso 6: Modificar mongodbDAOFactory
Esta clase se encarga de implementar la interfaz `interfaceDAOFactory`, devolviendo instancias concretas de DAOs basadas en MongoDB.
Define los métodos:
- `get_dao()` → devuelve un `MongodbDAO` ya conectado a su colección.

## ✅ Paso 7: Modificar Model
Esta clase se encarga de ser el intermediario entre el controlador y los DAOs. Utiliza una `DAOFactory` para acceder a la base de datos sin acoplarse a la tecnología (MongoDB, Firebase, etc.).
Define los métodos que llaman a la Factory para obtener un DAO y devolver los datos necesarios al controlador.

## ✅ Paso 8: Modificar Controller
Esta clase se encarga de recibir las peticiones HTTP del cliente (navegador, app, Postman, etc.) y delegar la lógica al modelo.  
Define:
- Endpoints HTTP (`GET`, `POST`, etc.)
- Funciones que llaman a métodos del modelo para obtener o modificar datos.

## ✅ Paso 9: Modificar View
Esta clase se encarga de la presentación de los datos. Es decir, cómo se muestran al usuario (por ejemplo, en una plantilla HTML o en formato JSON).  
Es útil especialmente si estás construyendo una aplicación web con vistas renderizadas (no solo una API).
Define:
- Métodos que reciben datos del controlador y los formatean o presentan usando plantillas (por ejemplo, con Jinja2).
- En proyectos tipo API, también puede devolver datos formateados directamente.