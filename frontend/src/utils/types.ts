export interface ShoppingItem {
  id: number;
  text: string;
}

export interface Product {
  original_term: string;
  searched_term: string;
  name: string;
  price: number;
  is_discounted: boolean;
  url: string;
}

export interface ShopResult {
  products: Product[];
  total: number;
}

export interface CheapestResult {
  shop: string;
  total: number;
  products: Product[];
}

export interface ShoppingListResponse {
  shopping_list: string[];
  complete_shops: Record<string, ShopResult>;
  cheapest: CheapestResult | null;
  shops_compared: number;
}
