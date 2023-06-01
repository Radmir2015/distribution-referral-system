from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List

# Import classes from the previous implementation
from referral_system import Referrer, Product, ReferralLink

app = FastAPI()

referrers = {}
products = {}
referral_links = {}


class ReferrerIn(BaseModel):
    name: str
    referral_percentage: float


class ProductIn(BaseModel):
    name: str
    price: float


class ReferralLinkIn(BaseModel):
    referrer_id: str
    product_id: str
    level: Optional[int] = 0
    children_ids: Optional[List[str]] = []


class ReferralLinkOut(BaseModel):
    id: str
    referrer_id: str
    product_id: str
    level: int
    children_ids: List[str]
    is_active: bool


@app.post("/referrers", status_code=201)
def create_referrer(referrer: ReferrerIn):
    new_referrer = Referrer(name=referrer.name, referral_percentage=referrer.referral_percentage)
    referrers[new_referrer.id] = new_referrer
    return new_referrer


@app.post("/products", status_code=201)
def create_product(product: ProductIn):
    new_product = Product(name=product.name, price=product.price)
    products[new_product.id] = new_product
    return new_product


@app.post("/referral_links", status_code=201)
def create_referral_link(referral_link: ReferralLinkIn):
    if referral_link.referrer_id not in referrers:
        raise HTTPException(status_code=404, detail="Referrer not found")
    if referral_link.product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    referrer = referrers[referral_link.referrer_id]
    product = products[referral_link.product_id]

    new_referral_link = ReferralLink(referrer=referrer, product=product, level=referral_link.level, is_active=True)

    for child_id in referral_link.children_ids:
        if child_id not in referral_links:
            raise HTTPException(status_code=404, detail=f"Referral link with id {child_id} not found")
        new_referral_link.add_child(referral_links[child_id])

    referral_links[new_referral_link.id] = new_referral_link
    return ReferralLinkOut(id=new_referral_link.id,
                           referrer_id=new_referral_link.referrer.id,
                           product_id=new_referral_link.product.id,
                           level=new_referral_link.level,
                           children_ids=[child.id for child in new_referral_link.children],
                           is_active=new_referral_link.is_active)


@app.patch("/referral_links/{referral_link_id}/activate")
def activate_referral_link(referral_link_id: str):
    if referral_link_id not in referral_links:
        raise HTTPException(status_code=404, detail="Referral link not found")

    referral_links[referral_link_id].is_active = True
    return {"status": "Referral link activated"}


@app.patch("/referral_links/{referral_link_id}/deactivate")
def deactivate_referral_link(referral_link_id: str):
    if referral_link_id not in referral_links:
        raise HTTPException(status_code=404, detail="Referral link not found")

    referral_links[referral_link_id].is_active = False
    return {"status": "Referral link deactivated"}


@app.get("/referral_links/{referral_link_id}/commission")
def get_commission(referral_link_id: str):
    if referral_link_id not in referral_links:
        raise HTTPException(status_code=404, detail="Referral link not found")

    if not referral_links[referral_link_id].is_active:
        raise HTTPException(status_code=403, detail="Referral link is not active")

    referral_link = referral_links[referral_link_id]
    commission = referral_link.calculate_commission()
    return {"commission": commission}

@app.get("/referral_links/{referral_link_id}/click")
def handle_click(referral_link_id: str):
    if referral_link_id not in referral_links:
        raise HTTPException(status_code=404, detail="Referral link not found")

    referral_link = referral_links[referral_link_id]

    if not referral_link.is_active:
        raise HTTPException(status_code=403, detail="Referral link is not active")

    # Increase click count for the referral link
    referral_link.clicks += 1

    # Increase the referrer's balance by the calculated commission
    commission = referral_link.calculate_commission()
    referral_link.referrer.balance += commission

    return {"status": "Referral reward processed", "referrer_balance": referral_link.referrer.balance}