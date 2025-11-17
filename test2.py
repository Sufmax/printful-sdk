#!/usr/bin/env python3
"""
Script de démonstration du SDK Printful
Montre l'utilisation basique avec des méthodes non-sensibles
"""

import os
import json
import base64
import requests
from pathlib import Path
from printful_sdk import PrintfulSDK


def download_and_save_image(url: str, filepath: str) -> bool:
    """
    Télécharge une image depuis une URL et la sauvegarde localement
    
    Args:
        url: URL de l'image à télécharger
        filepath: Chemin complet où sauvegarder l'image
    
    Returns:
        True si succès, False sinon
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Créer le répertoire parent s'il n'existe pas
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        # Sauvegarder l'image
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"      ❌ Erreur lors du téléchargement de {url}: {e}")
        return False


def save_base64_image(base64_data: str, filepath: str) -> bool:
    """
    Sauvegarde une image encodée en base64
    
    Args:
        base64_data: Données de l'image en base64
        filepath: Chemin complet où sauvegarder l'image
    
    Returns:
        True si succès, False sinon
    """
    try:
        # Retirer le préfixe data:image/xxx;base64, s'il existe
        if ',' in base64_data:
            base64_data = base64_data.split(',')[1]
        
        # Décoder et sauvegarder
        image_data = base64.b64decode(base64_data)
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(image_data)
        
        return True
    except Exception as e:
        print(f"      ❌ Erreur lors de la sauvegarde base64: {e}")
        return False


def truncate_text(text: str, max_length: int = 50) -> str:
    """Tronque un texte à la longueur maximale spécifiée"""
    if not text:
        return ""
    return text[:max_length] + "..." if len(text) > max_length else text


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
        
        # 4. Si des produits existent, récupérer les détails complets
        if products_list:
            for idx, product_summary in enumerate(products_list[:2], 1):  # Limiter à 2 produits pour la démo
                product_id = product_summary['id']
                product_title = product_summary.get('title', 'Sans titre')
                
                print(f"\n4.{idx}. Analyse détaillée du produit ID {product_id}: {product_title}")
                print("=" * 60)
                
                # Récupérer les détails complets du produit
                product_details = sdk.get_product(product_id)
                product_info = product_details.get('result', {}).get('product', {})
                variants = product_details.get('result', {}).get('variants', [])
                
                # Description du produit (limitée à 50 caractères)
                description = product_info.get('description', 'Aucune description disponible')
                print(f"   📝 Description: {truncate_text(description, 50)}")
                
                # Analyse des variantes pour prix et couleurs
                print(f"\n   💰 Analyse des {len(variants)} variantes:")
                
                # Collecter les prix et couleurs uniques
                prices = set()
                colors = set()
                sizes = set()
                
                for variant in variants[:10]:  # Limiter l'affichage à 10 variantes
                    # Prix
                    price = variant.get('price', 'N/A')
                    if price != 'N/A':
                        prices.add(float(price))
                    
                    # Couleur (peut être dans le nom ou les attributs)
                    variant_name = variant.get('name', '')
                    color = variant.get('color', '')
                    color_code = variant.get('color_code', '')
                    color_code2 = variant.get('color_code2', '')
                    
                    if color:
                        colors.add(color)
                    
                    # Taille
                    size = variant.get('size', '')
                    if size:
                        sizes.add(size)
                    
                    # Afficher quelques détails de variante
                    in_stock = variant.get('in_stock', False)
                    stock_status = "✅ En stock" if in_stock else "❌ Rupture"
                    print(f"      - {variant_name}: ${price} {stock_status}")
                    if color:
                        print(f"        Couleur: {color} {f'({color_code})' if color_code else ''}")
                
                # Résumé des prix
                if prices:
                    print(f"\n   💵 Gamme de prix: ${min(prices):.2f} - ${max(prices):.2f}")
                
                # Résumé des couleurs
                if colors:
                    colors_list = list(colors)[:10]  # Limiter à 10 couleurs
                    print(f"   🎨 Couleurs disponibles ({len(colors)} total): {', '.join(colors_list)}")
                
                # Résumé des tailles
                if sizes:
                    sizes_list = list(sizes)[:10]
                    print(f"   📏 Tailles disponibles: {', '.join(sizes_list)}")
                
                # 5. Téléchargement et sauvegarde des images
                print(f"\n   🖼️  Gestion des images du produit {product_id}:")
                
                # Créer le répertoire pour les images
                image_dir = Path(f"files/images/{product_id}")
                image_dir.mkdir(parents=True, exist_ok=True)
                
                # Sauvegarder les métadonnées du produit
                metadata_file = image_dir / "product_info.json"
                with open(metadata_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'id': product_id,
                        'title': product_title,
                        'description': description,
                        'colors': list(colors),
                        'sizes': list(sizes),
                        'price_range': {
                            'min': float(min(prices)) if prices else None,
                            'max': float(max(prices)) if prices else None
                        }
                    }, f, indent=2, ensure_ascii=False)
                print(f"      ✅ Métadonnées sauvegardées dans {metadata_file}")
                
                # Récupérer et sauvegarder les images
                images_saved = 0
                
                # Images depuis le produit principal
                product_files = product_info.get('files', [])
                for file_idx, file_info in enumerate(product_files):
                    if isinstance(file_info, dict):
                        file_url = file_info.get('url') or file_info.get('preview_url')
                        file_type = file_info.get('type', 'default')
                        
                        if file_url:
                            # Déterminer l'extension
                            ext = '.jpg'
                            if 'png' in file_url.lower():
                                ext = '.png'
                            elif 'gif' in file_url.lower():
                                ext = '.gif'
                            
                            filename = f"product_{file_type}_{file_idx}{ext}"
                            filepath = image_dir / filename
                            
                            print(f"      📥 Téléchargement de {filename}...")
                            if download_and_save_image(file_url, str(filepath)):
                                images_saved += 1
                                print(f"         ✅ Sauvegardé: {filepath}")
                    elif isinstance(file_info, str):
                        # Si c'est une URL directe
                        ext = '.jpg'
                        if 'png' in file_info.lower():
                            ext = '.png'
                        
                        filename = f"product_image_{file_idx}{ext}"
                        filepath = image_dir / filename
                        
                        print(f"      📥 Téléchargement de {filename}...")
                        if download_and_save_image(file_info, str(filepath)):
                            images_saved += 1
                            print(f"         ✅ Sauvegardé: {filepath}")
                
                # Images depuis les variantes (souvent des mockups)
                for var_idx, variant in enumerate(variants[:5]):  # Limiter pour la démo
                    variant_files = variant.get('files', [])
                    variant_id = variant.get('id')
                    
                    for file_idx, file_info in enumerate(variant_files):
                        if isinstance(file_info, dict):
                            file_url = file_info.get('url') or file_info.get('preview_url')
                            file_type = file_info.get('type', 'preview')
                            
                            if file_url:
                                ext = '.jpg'
                                if 'png' in file_url.lower():
                                    ext = '.png'
                                
                                filename = f"variant_{variant_id}_{file_type}_{file_idx}{ext}"
                                filepath = image_dir / filename
                                
                                print(f"      📥 Téléchargement de {filename}...")
                                if download_and_save_image(file_url, str(filepath)):
                                    images_saved += 1
                                    print(f"         ✅ Sauvegardé: {filepath}")
                
                # Image principale du produit si disponible
                if product_info.get('image'):
                    image_url = product_info['image']
                    filename = f"product_main.jpg"
                    filepath = image_dir / filename
                    
                    print(f"      📥 Téléchargement de l'image principale...")
                    if download_and_save_image(image_url, str(filepath)):
                        images_saved += 1
                        print(f"         ✅ Sauvegardé: {filepath}")
                
                # Thumbnail si disponible
                if product_info.get('thumbnail_url') or product_summary.get('thumbnail_url'):
                    thumb_url = product_info.get('thumbnail_url') or product_summary.get('thumbnail_url')
                    filename = f"product_thumbnail.jpg"
                    filepath = image_dir / filename
                    
                    print(f"      📥 Téléchargement de la miniature...")
                    if download_and_save_image(thumb_url, str(filepath)):
                        images_saved += 1
                        print(f"         ✅ Sauvegardé: {filepath}")
                
                print(f"\n   📊 Résumé: {images_saved} images sauvegardées dans {image_dir}")
                print("=" * 60)
        
        # 6. Récupérer le guide des tailles
        if products_list:
            first_product = products_list[0]
            product_id = first_product['id']
            try:
                print(f"\n5. Guide des tailles du produit {product_id}...")
                sizes = sdk.get_product_sizes(product_id)
                available_sizes = sizes.get('result', {}).get('available_sizes', [])
                print(f"   Tailles disponibles: {', '.join(available_sizes)}")
            except Exception as e:
                print(f"   Guide des tailles non disponible: {e}")
        
        # 7. Récupérer les boutiques (si applicable)
        print("\n6. Récupération des boutiques...")
        try:
            stores = sdk.get_stores()
            stores_list = stores.get('result', [])
            print(f"   Nombre de boutiques: {len(stores_list)}")
            for store in stores_list[:3]:  # Afficher max 3 boutiques
                print(f"   - {store.get('name', 'Sans nom')} (ID: {store.get('id')})")
        except Exception as e:
            print(f"   Impossible de récupérer les boutiques: {e}")
        
        # 8. Démonstration d'une opération sensible (désactivée)
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
    print(f"📁 Les images téléchargées sont disponibles dans le dossier 'files/images/'")


if __name__ == "__main__":
    main()
  
