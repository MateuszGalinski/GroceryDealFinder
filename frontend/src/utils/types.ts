export interface ShoppingItem {
  id: number;
  text: string;
}

export interface Product {
  id: number;
  url: string;
  name: string;
  price: number;
  is_discounted: boolean;
  discounted_price?: number;
}

export interface ShoppingListResponse {
  shop: string;
  products: Product[];
}
