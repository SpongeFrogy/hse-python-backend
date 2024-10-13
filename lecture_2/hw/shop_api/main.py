from fastapi import FastAPI, HTTPException
from http import HTTPStatus
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any
from http import HTTPStatus
from .models import Item, Cart, CreateItem

app = FastAPI(title="Shop API")

__items: Dict[int, Item] = {}
__carts: Dict[int, Cart] = {}

@app.post("/item")
def create_item(item: CreateItem) -> JSONResponse:
    new_id = len(__items) + 1
    new_item = Item(id=new_id, name=item.name, price=item.price)
    __items[new_id] = new_item
    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content=new_item.as_responce(),
        headers={"Location": f"/item/{new_id}"},
    )

@app.get("/item/{id}")
def get_item(id: int) -> JSONResponse:
    if id not in __items or __items[id].deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=f"Item {id} not found or deleted")
    item = __items[id]
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=item.as_responce(),
    )

@app.get("/item")
def get_item_list(offset: int = 0,
                  limit: int = 10,
                  min_price: Optional[float] = None,
                  max_price: Optional[float] = None,
                  show_deleted: bool = False) -> JSONResponse:
    if offset < 0 or limit <= 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                            detail="Offset must be non-negative and limit positive")
    items = list(__items.values())
    
    if min_price:
        if min_price < 0:
            raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                                detail="Price must be a non-negative number")
        items = [item for item in items if item.price >= min_price]

    if max_price:
        if max_price < 0:
            raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                                detail="Price must be a non-negative number")
        items = [item for item in items if item.price <= max_price]

    if show_deleted:
        items = [item for item in items if not item.deleted]

    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=[item.as_responce() for item in items[offset:offset + limit]],
    )

@app.put("/item/{id}")
def update_item(id: int, item: CreateItem) -> JSONResponse:
    if id not in __items:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Item not found")
    updated_item = Item(id=id, name=item.name, price=item.price)
    __items[id] = updated_item
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=updated_item.as_responce(),
    )

@app.patch("/item/{id}")
def patch_item(id: int, fields: dict[str, Any]) -> JSONResponse:
    if id not in __items:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Item not found")
    item = __items[id]
    if item.deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_MODIFIED, detail="Item is deleted")
    allowed_fields = {"name", "price"}
    if any(field not in allowed_fields for field in fields):
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY, detail="Invalid field in request body")
    updated_item = Item(
        id=id,
        name=fields.get("name", item.name),
        price=fields.get("price", item.price),
        # deleted=item.deleted
    )
    __items[id] = updated_item
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=updated_item.as_responce(),
    )


@app.delete("/item/{id}")
def delete_item(id: int) -> JSONResponse:
    if id not in __items:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Item not found")
    __items[id].deleted = True
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content={"message": "Item marked as deleted"},
    )

@app.post("/cart")
def create_cart() -> JSONResponse:
    new_id = len(__carts) + 1
    new_cart = Cart(id=new_id)
    __carts[new_id] = new_cart
    return JSONResponse(
        status_code=HTTPStatus.CREATED,
        content={"id": new_id},
        headers={"Location": f"/cart/{new_id}"},
    )

@app.get("/cart/{id}")
def get_cart(id: int) -> JSONResponse:
    if id not in __carts:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Cart not found")
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=__carts[id].as_responce(),
    )

@app.get("/cart")
def get_cart_list(offset: int = 0,
                  limit: int = 10,
                  min_price: Optional[float] = None,
                  max_price: Optional[float] = None,
                  min_quantity: Optional[int] = None,
                  max_quantity: Optional[int] = None) -> JSONResponse:
    if offset < 0 or limit <= 0:
        raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                            detail="Offset must be non-negative and limit positive")
    
    if min_price is not None and min_price < 0:
            raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                                detail="Price must be a non-negative number")

    if max_price is not None and max_price < 0:
            raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                                detail="Price must be a non-negative number")

    if min_quantity is not None and min_quantity < 0:
            raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                                detail="Quantity must be a non-negative number")

    if max_quantity is not None and max_quantity < 0:
            raise HTTPException(status_code=HTTPStatus.UNPROCESSABLE_ENTITY,
                                detail="Quantity must be a non-negative number")
    filtered_carts = [cart for cart in list(__carts.values())[offset:offset + limit]
                      if (min_price is None or cart.price >= min_price) and
                      (max_price is None or cart.price <= max_price) and
                      (min_quantity is None or sum(item.quantity for item in cart.items) >= min_quantity) and
                      (max_quantity is None or sum(item.quantity for item in cart.items) <= max_quantity)]
    
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=[curr_chart.as_responce() for curr_chart in filtered_carts],
    )

@app.post("/cart/{cart_id}/add/{item_id}")
def add_to_cart(cart_id: int, item_id: int) -> JSONResponse:
    if cart_id not in __carts:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Cart not found")
    if item_id not in __items or __items[item_id].deleted:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Item not found or deleted")
    item = __items[item_id]
    cart = __carts[cart_id]
    cart.add(item)
    return JSONResponse(
        status_code=HTTPStatus.OK,
        content=cart.as_responce(),
    )

