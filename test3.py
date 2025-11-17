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


def extract_and_download_all_images(data: dict, base_path: Path, prefix: str = "") -> int:
    """
    Fonction récursive pour extraire et télécharger TOUTES les images d'une structure de données
    
    Args:
        data: Dictionnaire ou liste contenant potentiellement des URLs d'images
        base_path: Chemin de base où sauvegarder les images
        prefix: Préfixe pour les noms de fichiers
    
    Returns:
        Nombre d'images téléchargées
    """
    images_downloaded = 0
    image_counter = 0
    
    # Liste des clés connues pouvant contenir des URLs d'images
    image_keys = [
        'url', 'preview_url', 'image', 'thumbnail', 'thumbnail_url',
        'src', 'image_url', 'file_url', 'mockup_url', 'preview',
        'large_url', 'medium_url', 'small_url', 'original_url'
    ]
    
    def process_url(url: str, name_hint: str = "") -> bool:
        nonlocal images_downloaded, image_counter
        
        if not url or not isinstance(url, str):
            return False
        
        # Ignorer les URLs non-HTTP
        if not url.startswith(('http://', 'https://')):
            # Vérifier si c'est du base64
            if url.startswith('data:image'):
                image_counter += 1
                ext = '.png'
                if 'jpeg' in url or 'jpg' in url:
                    ext = '.jpg'
                elif 'gif' in url:
                    ext = '.gif'
                
                filename = f"{prefix}_{name_hint}_{image_counter}{ext}" if name_hint else f"{prefix}_base64_{image_counter}{ext}"
                filepath = base_path / filename
                
                print(f"      📥 Sauvegarde image base64: {filename}")
                if save_base64_image(url, str(filepath)):
                    images_downloaded += 1
                    return True
            return False
        
        # Déterminer l'extension depuis l'URL
        ext = '.jpg'
        url_lower = url.lower()
        if '.png' in url_lower:
            ext = '.png'
        elif '.gif' in url_lower:
            ext = '.gif'
        elif '.webp' in url_lower:
            ext = '.webp'
        elif '.jpeg' in url_lower or '.jpg' in url_lower:
            ext = '.jpg'
        
        image_counter += 1
        filename = f"{prefix}_{name_hint}_{image_counter}{ext}" if name_hint else f"{prefix}_image_{image_counter}{ext}"
        filepath = base_path / filename
        
        # Éviter les doublons
        if filepath.exists():
            return False
        
        print(f"      📥 Téléchargement: {filename}")
        if download_and_save_image(url, str(filepath)):
            images_downloaded += 1
            return True
        return False
    
    # Explorer récursivement la structure de données
    if isinstance(data, dict):
        for key, value in data.items():
            # Si la clé suggère une image
            if any(img_key in key.lower() for img_key in image_keys):
                if isinstance(value, str):
                    process_url(value, key)
                elif isinstance(value, list):
                    for idx, item in enumerate(value):
                        if isinstance(item, str):
                            process_url(item, f"{key}_{idx}")
                        elif isinstance(item, dict):
                            images_downloaded += extract_and_download_all_images(
                                item, base_path, f"{prefix}_{key}_{idx}"
                            )
            # Continuer la recherche récursive
            elif isinstance(value, (dict, list)):
                images_downloaded += extract_and_download_all_images(
                    value, base_path, prefix
                )
    
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            if isinstance(item, dict):
                images_downloaded += extract_and_download_all_images(
                    item, base_path, f"{prefix}_{idx}"
                )
            elif isinstance(item, str):
                # Vérifier si c'est une URL
                if item.startswith(('http://', 'https://', 'data:image')):
                    process_url(item, f"item_{idx}")
    
    return images_downloaded


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
                
                # Analyser TOUTES les variantes
                for variant in variants:
                    # Prix
                    price = variant.get('price', 'N/A')
                    if price != 'N/A':
                        prices.add(float(price))
                    
                    # Couleur (peut être dans le nom ou les attributs)
                    color = variant.get('color', '')
                    color_code = variant.get('color_code', '')
                    
                    if color:
                        colors.add(color)
                    
                    # Taille
                    size = variant.get('size', '')
                    if size:
                        sizes.add(size)
                
                # Afficher quelques exemples de variantes (limité pour lisibilité)
                print(f"   Exemples de variantes (sur {len(variants)} total):")
                for variant in variants[:5]:
                    variant_name = variant.get('name', '')
                    price = variant.get('price', 'N/A')
                    in_stock = variant.get('in_stock', False)
                    stock_status = "✅" if in_stock else "❌"
                    print(f"      - {variant_name}: ${price} {stock_status}")
                
                # Résumé des prix
                if prices:
                    print(f"\n   💵 Gamme de prix: ${min(prices):.2f} - ${max(prices):.2f}")
                
                # Résumé des couleurs
                if colors:
                    print(f"   🎨 {len(colors)} couleurs disponibles: {', '.join(list(colors)[:10])}")
                    if len(colors) > 10:
                        print(f"      ... et {len(colors) - 10} autres couleurs")
                
                # Résumé des tailles
                if sizes:
                    print(f"   📏 Tailles disponibles: {', '.join(sorted(sizes))}")
                
                # 5. TÉLÉCHARGEMENT DE TOUTES LES IMAGES
                print(f"\n   🖼️  TÉLÉCHARGEMENT DE TOUTES LES IMAGES DU PRODUIT {product_id}:")
                print("   " + "-" * 50)
                
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
                        'total_variants': len(variants),
                        'colors': list(colors),
                        'sizes': list(sizes),
                        'price_range': {
                            'min': float(min(prices)) if prices else None,
                            'max': float(max(prices)) if prices else None
                        }
                    }, f, indent=2, ensure_ascii=False)
                print(f"   ✅ Métadonnées sauvegardées dans {metadata_file}")
                
                # Méthode 1: Extraction exhaustive depuis toute la structure de données
                print("\n   🔍 Recherche exhaustive de TOUTES les images...")
                total_images = 0
                
                # Images du produit principal
                print("   📦 Images du produit principal:")
                product_images = extract_and_download_all_images(
                    product_info,
                    image_dir,
                    "product"
                )
                total_images += product_images
                print(f"      → {product_images} images trouvées")
                
                # Images de TOUTES les variantes
                print(f"\n   🎯 Images des {len(variants)} variantes:")
                for v_idx, variant in enumerate(variants):
                    variant_id = variant.get('id', f'unknown_{v_idx}')
                    variant_name = variant.get('name', '').replace('/', '_').replace('\\', '_')[:50]
                    
                    # Créer un sous-dossier pour cette variante
                    variant_dir = image_dir / f"variant_{variant_id}"
                    variant_dir.mkdir(exist_ok=True)
                    
                    variant_images = extract_and_download_all_images(
                        variant,
                        variant_dir,
                        f"v{variant_id}"
                    )
                    
                    if variant_images > 0:
                        print(f"      Variante {variant_id} ({variant_name}): {variant_images} images")
                        total_images += variant_images
                
                # Méthode 2: Recherche additionnelle dans le résumé initial
                print("\n   🔄 Recherche d'images additionnelles dans le résumé...")
                summary_images = extract_and_download_all_images(
                    product_summary,
                    image_dir,
                    "summary"
                )
                total_images += summary_images
                print(f"      → {summary_images} images supplémentaires trouvées")
                
                # Essayer de récupérer les templates de mockup si disponibles
                print("\n   🎨 Tentative de récupération des mockups...")
                try:
                    mockup_printfiles = sdk.get_mockup_printfiles(product_id)
                    mockup_images = extract_and_download_all_images(
                        mockup_printfiles,
                        image_dir / "mockups",
                        "mockup"
                    )
                    total_images += mockup_images
                    print(f"      → {mockup_images} mockups trouvés")
                except:
                    print("      → Pas de mockups disponibles")
                
                # Essayer de récupérer les templates
                try:
                    templates = sdk.get_mockup_templates(product_id)
                    template_images = extract_and_download_all_images(
                        templates,
                        image_dir / "templates",
                        "template"
                    )
                    total_images += template_images
                    print(f"      → {template_images} templates trouvés")
                except:
                    print("      → Pas de templates disponibles")
                
                # Statistiques finales
                print("\n   " + "=" * 50)
                print(f"   📊 TOTAL: {total_images} images téléchargées")
                print(f"   📁 Emplacement: {image_dir.absolute()}")
                
                # Lister les sous-dossiers créés
                subdirs = [d for d in image_dir.iterdir() if d.is_dir()]
                if subdirs:
                    print(f"   📂 Sous-dossiers créés: {len(subdirs)}")
                    for subdir in subdirs[:5]:
                        file_count = len(list(subdir.glob('*')))
                        print(f"      - {subdir.name}: {file_count} fichiers")
                
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
    print(f"📁 TOUTES les images téléchargées sont disponibles dans le dossier 'files/images/'")
    
    # Afficher le résumé final des téléchargements
    try:
        total_files = 0
        for root, dirs, files in os.walk("files/images/"):
            total_files += len([f for f in files if f.endswith(('.jpg', '.png', '.gif', '.webp'))])
        print(f"📊 Total global: {total_files} images dans tous les dossiers")
    except:
        pass


if __name__ == "__main__":
    main()
