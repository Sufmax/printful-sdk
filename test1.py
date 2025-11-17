#!/usr/bin/env python3
"""
Script de démonstration du SDK Printful
Montre l'utilisation basique avec des méthodes non-sensibles
"""

from printful_sdk import PrintfulSDK


def main():
    # Initialisation du SDK
    # Note: Remplacez 'YOUR_API_KEY' par votre clé API réelle
    sdk = PrintfulSDK(api_key='YOUR_API_KEY')
    
    # Alternative: Définir la clé API après initialisation
    # sdk = PrintfulSDK()
    # sdk.set_api_key('YOUR_API_KEY')
    
    # Si vous utilisez un token Account-level, définissez le store_id
    # sdk.set_store_id(123456)
    
    print("=== Démonstration du SDK Printful ===\n")
    
    try:
        # 1. Récupérer les scopes OAuth
        print("1. Récupération des scopes OAuth...")
        scopes = sdk.get_oauth_scopes()
        print(f"   Nombre de scopes: {len(scopes.get('result', {}).get('scopes', []))}")
        
        # 2. Récupérer les catégories de produits
        print("\n2. Récupération des catégories...")
        categories = sdk.get_categories()
        print(f"   Nombre de catégories: {len(categories.get('result', []))}")
        
        # 3. Récupérer les premiers produits du catalogue
        print("\n3. Récupération des produits...")
        products = sdk.get_products(limit=5)
        products_list = products.get('result', [])
        print(f"   Nombre de produits récupérés: {len(products_list)}")
        
        # 4. Si des produits existent, récupérer les détails du premier
        if products_list:
            first_product = products_list[0]
            product_id = first_product['id']
            print(f"\n4. Détails du produit ID {product_id}: {first_product['title']}")
            
            product_details = sdk.get_product(product_id)
            variants = product_details.get('result', {}).get('variants', [])
            print(f"   Nombre de variantes: {len(variants)}")
            
            # 5. Récupérer le guide des tailles si disponible
            try:
                print(f"\n5. Guide des tailles du produit {product_id}...")
                sizes = sdk.get_product_sizes(product_id)
                available_sizes = sizes.get('result', {}).get('available_sizes', [])
                print(f"   Tailles disponibles: {', '.join(available_sizes)}")
            except Exception as e:
                print(f"   Guide des tailles non disponible: {e}")
        
        # 6. Récupérer les boutiques (si applicable)
        print("\n6. Récupération des boutiques...")
        try:
            stores = sdk.get_stores()
            stores_list = stores.get('result', [])
            print(f"   Nombre de boutiques: {len(stores_list)}")
            for store in stores_list[:3]:  # Afficher max 3 boutiques
                print(f"   - {store.get('name', 'Sans nom')} (ID: {store.get('id')})")
        except Exception as e:
            print(f"   Impossible de récupérer les boutiques: {e}")
        
        # 7. Démonstration d'une opération sensible (désactivée)
        print("\n7. Test d'une opération sensible...")
        print("   Tentative de création de commande (désactivée pour sécurité):")
        
        mock_recipient = {
            "name": "John Doe",
            "address1": "123 Main St",
            "city": "Los Angeles",
            "state_code": "CA",
            "country_code": "US",
            "zip": "90001"
        }
        
        mock_items = [{
            "variant_id": 1,
            "quantity": 1
        }]
        
        result = sdk.create_order(
            recipient=mock_recipient,
            items=mock_items
        )
        print(f"   Résultat simulé: {result}")
        
    except Exception as e:
        print(f"\n❌ Erreur lors de l'exécution: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n=== Fin de la démonstration ===")


if __name__ == "__main__":
    main()
