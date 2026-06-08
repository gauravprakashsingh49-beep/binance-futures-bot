import random

class FoodOrderingAgent:
    def __init__(self):
        # Simulated menu for different food categories
        self.menu = {
            "pizza": ["Margherita", "Pepperoni", "Veggie Supreme", "BBQ Chicken"],
            "burger": ["Cheese Burger", "Chicken Burger", "Veggie Burger", "Bacon Burger"],
            "pasta": ["Carbonara", "Pesto", "Alfredo", "Arrabbiata"],
            "salad": ["Caesar Salad", "Greek Salad", "Garden Salad"],
            "drink": ["Coke", "Sprite", "Orange Juice", "Water"]
        }
        self.available_restaurants = ["Pizza Palace", "Burger Barn", "Pasta Place", "Healthy Eats"]

    def parse_requirement(self, user_input):
        """
        Simple NLP-like parsing to identify food category and preferences
        """
        user_input_lower = user_input.lower()
        
        # Check for food categories
        for category in self.menu.keys():
            if category in user_input_lower:
                # Randomly select an item from the category
                item = random.choice(self.menu[category])
                return category, item
        
        # If no category found, try to match specific items
        for category, items in self.menu.items():
            for item in items:
                if item.lower() in user_input_lower:
                    return category, item
        
        return None, None

    def get_restaurant(self):
        """
        Randomly select a restaurant for the order
        """
        return random.choice(self.available_restaurants)

    def calculate_price(self, category, item):
        """
        Simulate price calculation
        """
        base_prices = {
            "pizza": 12.99,
            "burger": 8.99,
            "pasta": 10.99,
            "salad": 7.99,
            "drink": 2.99
        }
        return base_prices.get(category, 9.99)

    def place_order(self, user_input):
        """
        Main method to process the order
        """
        print("🤖 AI Food Ordering Agent activated!")
        print("Processing your request: " + user_input)
        print("-" * 40)
        
        category, item = self.parse_requirement(user_input)
        
        if category and item:
            restaurant = self.get_restaurant()
            price = self.calculate_price(category, item)
            order_id = random.randint(10000, 99999)
            
            print(f"✅ Order Details:")
            print(f"   Restaurant: {restaurant}")
            print(f"   Item: {item} ({category.capitalize()})")
            print(f"   Price: ${price:.2f}")
            print(f"   Order ID: #{order_id}")
            print(f"   Estimated delivery: 30-45 minutes")
            print("-" * 40)
            print("🎉 Order placed successfully! Your food is on the way!")
            
            return {
                "order_id": order_id,
                "restaurant": restaurant,
                "item": item,
                "category": category,
                "price": price
            }
        else:
            print("❌ Sorry, I couldn't understand your food request.")
            print("   Please try mentioning: pizza, burger, pasta, salad, or drink")
            print("   Example: 'I want a pepperoni pizza' or 'Order me a cheese burger'")
            return None

def main():
    """
    Main function to run the food ordering agent
    """
    agent = FoodOrderingAgent()
    
    print("🍕 Welcome to the AI Food Ordering Assistant!")
    print("Tell me what you'd like to order.")
    print("Example: 'I want pizza' or 'Order me a burger'")
    print("-" * 50)
    
    while True:
        user_input = input("Your order: ").strip()
        
        if user_input.lower() in ['quit', 'exit', 'bye']:
            print("👋 Thank you for using the AI Food Ordering Assistant. Goodbye!")
            break
        
        if user_input:
            order_result = agent.place_order(user_input)
            if order_result:
                # Could save order history here
                pass
        else:
            print("Please enter your food order request.")
        
        print()  # Empty line for readability

if __name__ == "__main__":
    main()