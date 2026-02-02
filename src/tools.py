from src.database import get_cursor

def search_products(query=None, max_price=None, min_rating=None, category=None):
    print(f"SEARCH TOOL: query={query}, max_price={max_price}, min_rating={min_rating}, category={category}")

    with get_cursor(commit=False) as cursor:
        sql = "SELECT * FROM products WHERE stock_quantity > 0"
        params = []

        if query:
            sql += " AND (name ILIKE %s OR brand ILIKE %s OR processor ILIKE %s OR gpu ILIKE %s)"
            search_term = f"%{query}%"
            params.extend([search_term] * 4)
        
        if max_price:
            sql += " AND price <= %s"
            params.append(max_price)
        
        if min_rating:
            sql += " AND customer_rating >= %s"
            params.append(min_rating)
        
        if category:
            sql += " AND category = %s"
            params.append(category)
        
        sql += " ORDER BY customer_rating DESC, price ASC LIMIT 5"

        cursor.execute(sql, params)
        results = cursor.fetchall()

        if not results:
            return "No products found matching your criteria. Try adjusting your search parameters."
        
        products_info = []

        for row in results:
            products_info.append(
                f"- {row[1]} - ${float(row[8]):.2f} | {row[3]} | {row[4]}GB RAM | "
                f"{row[5]}GB {row[6]} | {row[7]} | Rating: {float(row[10])}⭐ | Stock: {row[9]} units"
            )
        
        return f"Found {len(results)} product(s):\n" + "\n".join(products_info)

def get_product_details(product_name):
    print(f"DETAILS TOOL: product_name={product_name}", flush=True)

    with get_cursor(commit=False) as cursor:
        cursor.execute("""
        SELECT * FROM products
        WHERE name ILIKE %s
        LIMIT 1""", (f"%{product_name}%",))

        result = cursor.fetchone()

        if not result:
            return f"No details found for product '{product_name}' in our inventory."
        
        return f"""
Product: {result[1]}
Brand: {result[2]}
Processor: {result[3]}
RAM: {result[4]}GB
Storage: {result[5]}GB {result[6]}
GPU: {result[7]}
Price: ${float(result[8]):.2f}
In stock: {result[9]} units available
Customer rating: {float(result[10])}⭐ / 5.0
Category: {result[11]}
"""
    
def check_stock(product_name):
    print(f"STOCK TOOL: {product_name}", flush=True)

    with get_cursor(commit=False) as cursor:
        cursor.execute("""
        SELECT name, stock_quantity, price FROM products
        WHERE name ILIKE %s
        LIMIT 1""", (f"%{product_name}%",))
        
        result = cursor.fetchone()

        if not result:
            return f"Product '{product_name}' not found."
        
        name, stock, price = result

        if stock > 10:
            status = "In stock (plenty available)"
        elif stock > 0:
            status = f"Limited stock ({stock} units left)"
        else:
            status = "Out of stock"
        
        return f"{name} : {status} | Price: ${float(price):.2f}"


def get_budget_recommendations(budget, category=None):
    print(f"BUDGET TOOL: budget=${budget}, category={category}", flush=True)

    with get_cursor(commit=False) as cursor:
        sql = """
        SELECT name, price, customer_rating, processor, ram_gb, stock_quantity
        FROM products
        WHERE price <= %s AND stock_quantity > 0
        """
        params = [budget]

        if category:
            sql += " AND category = %s"
            params.append(category.lower())

        sql += " ORDER BY customer_rating DESC, price ASC LIMIT 3"

        cursor.execute(sql, params)
        results = cursor.fetchall()

        if not results:
            return f"No products found within a budget of ${budget}."
        
        recommendations = []
        for row in results:
            recommendations.append(
                f"- {row[0]} | Price: ${float(row[1]):.2f} | Rating: {float(row[2])}⭐ | "
                f"Specs: {row[3]}, {row[4]}GB RAM | Stock: {row[5]} units"
            )
        
        return f"Recommended products within your budget of ${budget}:\n" + "\n".join(recommendations)
    
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_products",
            "description": "Search for computer products based on criteria like keywords, price, rating, or category. Use this when customer asks to browse, search, or find products.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search keywords (e.g., 'gaming', 'Dell', 'RTX 4090', 'MacBook')"
                    },
                    "max_price": {
                        "type": "number",
                        "description": "Maximum price in USD"
                    },
                    "min_rating": {
                        "type": "number",
                        "description": "Minimum customer rating (0-5)"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["laptop", "desktop"],
                        "description": "Product category"
                    }
                },
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_product_details",
            "description": "Get detailed specifications and information about a specific product by name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the product to get details for"
                    }
                },
                "required": ["product_name"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_stock",
            "description": "Check stock availability for a specific product.",
            "parameters": {
                "type": "object",
                "properties": {
                    "product_name": {
                        "type": "string",
                        "description": "The name of the product to check stock for"
                    }
                },
                "required": ["product_name"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_budget_recommendations",
            "description": "Get recommended products within a specific budget. Use this when customer mentions their budget or asks for affordable options.",
            "parameters": {
                "type": "object",
                "properties": {
                    "budget": {
                        "type": "number",
                        "description": "Maximum budget in USD"
                    },
                    "category": {
                        "type": "string",
                        "enum": ["laptop", "desktop"],
                        "description": "Product category (optional)"
                    }
                },
                "required": ["budget"],
                "additionalProperties": False
            }
        }
    }
]