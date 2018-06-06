# Swagger info list
## Changes
### Bogdan

* `/clients/`
  * additional fields
  * del `is_legal`
* `/clients/type_faces/`
* `personal_list` -> `employees`
* `/clients/employee/`
  * (?) `_full_name` - зачем делать конкатинацию 3х строчек на сервере?
* del `/client/<id>/type/`
* `/cleints/groups/`
  * del `clientsList` - это перебор выгружать всех клиентов при запросе списка групп (если надо, то вернуть не проблема, но ...)
  * change `PUT` to `POST` (create action)
  * del `POST`
* add `/cleints/groups/<id>/ PUT` - update
  * `clientList` -> `client_list`
* move `/clients/tags/<id>/` to `/clients/tags/<id>/clients/` (clients list for given tag)
* `/cleints/<id>/tag/<id>/` 
  * `POST`/`DELETE` - response changed from detailed to short model
* add `/cleints/<id>/tag/ DELETE`
  
## Errors
* `boards/`
  * `cards/` - 404 Not Found (JSON Resp)
  * `archive/` - 404 Not Found (JSON Resp)
* `card/`
  * `storage/` - 404 Not Found (JSON Resp)
  * `storage/<type>` - 404 Not Found (HTML Resp)