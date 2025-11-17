# Printful SDK Python

## 1. Introduction

Bienvenue dans le SDK Python pour l'API Printful ! Ce SDK est une interface Python moderne et intuitive conçue pour simplifier l'interaction avec l'API Printful v1. Il encapsule toute la complexité des appels HTTP dans des méthodes Python élégantes, permettant aux développeurs d'intégrer rapidement les fonctionnalités de Printful dans leurs applications. Que vous souhaitiez gérer votre catalogue de produits, automatiser la création de commandes ou générer des mockups, ce SDK vous offre tous les outils nécessaires dans un package Python robuste et sécurisé.

## 2. Fonctionnalités (Features)

* **Interface orientée objet simple et intuitive** - Toutes les fonctionnalités de l'API sont accessibles via des méthodes Python claires et bien nommées
* **Gestion flexible de la clé API** - Configuration possible à l'initialisation ou dynamiquement via `set_api_key()`
* **Support complet multi-boutiques** - Gestion native des tokens Account-level avec header `X-PF-Store-Id`
* **Conversion automatique des IDs externes** - Le SDK gère automatiquement le préfixe `@` pour les external_ids
* **Gestion robuste des erreurs** - Exceptions HTTP natives de `requests` pour un debugging efficace
* **Sécurité renforcée** - Opérations financières sensibles désactivées par défaut avec alertes explicites
* **Pagination intégrée** - Support natif des paramètres `offset` et `limit` sur tous les endpoints de liste
* **Documentation inline complète** - Chaque méthode est documentée avec ses paramètres et types de retour
* **Compatibilité Python 3.6+** - Utilisation des type hints pour une meilleure expérience développeur

## 3. Installation

Le SDK ne nécessite qu'une seule dépendance externe : la bibliothèque `requests`. Installez-la simplement via pip :

``` 
pip install requests
```

Ensuite, téléchargez le fichier `printful_sdk.py` et placez-le dans votre projet. C'est tout ! Vous êtes prêt à commencer.

## 4. Démarrage Rapide (Quick Start)

Voici un exemple minimal pour démarrer avec le SDK :

```python
from printful_sdk import PrintfulSDK

# Initialiser le SDK avec votre clé API
sdk = PrintfulSDK(api_key='YOUR_API_KEY_HERE')

# Récupérer la liste de vos boutiques
stores = sdk.get_stores()

# Afficher les résultats
if stores['code'] == 200:
    print(f"Vous avez {len(stores['result'])} boutique(s) :")
    for store in stores['result']:
        print(f"  - {store['name']} (ID: {store['id']})")
else:
    print("Erreur lors de la récupération des boutiques")
```

## 5. Utilisation Détaillée

### Instanciation Alternative

Vous pouvez également instancier le SDK sans clé API et la configurer plus tard :

```python
from printful_sdk import PrintfulSDK

# Créer une instance sans clé API
sdk = PrintfulSDK()

# Configurer la clé API plus tard (par exemple après l'avoir récupérée d'un fichier de config)
api_key = load_api_key_from_config()  # Votre fonction
sdk.set_api_key(api_key)

# Pour les tokens Account-level, définissez également le store_id
sdk.set_store_id(123456)
```

### Appeler une méthode avec des paramètres

Voici un exemple plus complexe créant un produit synchronisé dans votre boutique :

```python
from printful_sdk import PrintfulSDK

sdk = PrintfulSDK(api_key='YOUR_API_KEY_HERE')

# Définir les données du produit
sync_product = {
    "name": "Mon T-Shirt Custom",
    "thumbnail": "https://example.com/thumbnail.jpg",
    "is_ignored": False
}

# Définir les variantes (avec fichiers d'impression)
sync_variants = [
    {
        "variant_id": 4012,  # Bella + Canvas 3001, Medium, White
        "retail_price": "29.99",
        "sku": "CUSTOM-001-M-WHITE",
        "files": [
            {
                "type": "default",  # Position d'impression (front)
                "url": "https://example.com/design-front.png"
            },
            {
                "type": "back",
                "url": "https://example.com/design-back.png"
            }
        ]
    },
    {
        "variant_id": 4013,  # Bella + Canvas 3001, Large, White  
        "retail_price": "29.99",
        "sku": "CUSTOM-001-L-WHITE",
        "files": [
            {
                "type": "default",
                "url": "https://example.com/design-front.png"
            }
        ]
    }
]

# Créer le produit
result = sdk.create_store_product(
    sync_product=sync_product,
    sync_variants=sync_variants
)

print(f"Produit créé avec succès ! ID: {result['result']['id']}")
print(f"Nombre de variantes créées : {result['result']['variants']}")
```

### Gestion des Erreurs

Une gestion appropriée des erreurs est essentielle. Voici comment intercepter et gérer les erreurs API :

```python
from printful_sdk import PrintfulSDK
import requests

sdk = PrintfulSDK(api_key='YOUR_API_KEY_HERE')

try:
    # Tentative de récupération d'un produit qui pourrait ne pas exister
    product_id = 99999
    product = sdk.get_product(product_id)
    print(f"Produit trouvé : {product['result']['product']['title']}")
    
except requests.exceptions.HTTPError as e:
    # Gestion des erreurs HTTP (404, 401, 500, etc.)
    if e.response.status_code == 404:
        print(f"Produit {product_id} introuvable")
    elif e.response.status_code == 401:
        print("Erreur d'authentification - Vérifiez votre clé API")
    elif e.response.status_code == 429:
        print("Limite de taux dépassée - Attendez avant de réessayer")
    else:
        print(f"Erreur HTTP {e.response.status_code}: {e.response.text}")
        
except requests.exceptions.ConnectionError:
    print("Impossible de se connecter à l'API Printful")
    
except requests.exceptions.Timeout:
    print("La requête a expiré - L'API met trop de temps à répondre")
    
except Exception as e:
    print(f"Erreur inattendue : {e}")
```

## 6. Note de Sécurité Importante

### ⚠️ Opérations Sensibles Désactivées

Pour votre protection, ce SDK **désactive intentionnellement** toutes les opérations financières et logistiques irréversibles. Les méthodes suivantes sont concernées :

* `create_order()` - Création de commandes réelles
* `confirm_order()` - Confirmation de commandes pour production
* `cancel_order()` - Annulation de commandes (peut déclencher des remboursements)

### Comportement des Méthodes Sécurisées

Lorsque vous appelez une méthode sensible, le SDK :
1. **N'exécute PAS** la requête HTTP réelle
2. Affiche un avertissement clair dans la console
3. Retourne une réponse simulée pour permettre le développement

### Exemple de Sortie Console

```python
from printful_sdk import PrintfulSDK

sdk = PrintfulSDK(api_key='YOUR_API_KEY_HERE')

# Tentative de création d'une commande
recipient = {
    "name": "Jane Smith",
    "address1": "456 Oak Street",
    "city": "New York",
    "state_code": "NY",
    "country_code": "US",
    "zip": "10001"
}

items = [
    {
        "variant_id": 4012,
        "quantity": 2,
        "retail_price": "29.99"
    }
]

# Cette méthode est sécurisée et ne créera PAS de commande réelle
result = sdk.create_order(recipient=recipient, items=items, confirm=True)
```

**Sortie console attendue :**
```
⚠️ ATTENTION: create_order() est une opération financière sensible - désactivée par sécurité
   Pour activer cette fonction, décommentez la ligne de requête dans le code source
```

**Réponse retournée (simulée) :**
```python
{
    "status": "mock_success",
    "message": "Operation deactivated for safety.",
    "mock_order_id": "12345"
}
```

### Réactiver les Opérations Sensibles

Si vous souhaitez réellement effectuer ces opérations en production :
1. Ouvrez le fichier `printful_sdk.py`
2. Localisez la méthode concernée (ex: `create_order`)
3. Décommentez la ligne contenant `response = self._make_request(...)`
4. Commentez ou supprimez la ligne de retour simulé

**⚠️ ATTENTION :** Ne réactivez ces méthodes qu'après avoir testé complètement votre intégration et être certain de vouloir effectuer des transactions réelles qui seront facturées.

---

## Support et Contribution

Ce SDK a été conçu pour être simple, sûr et extensible. Si vous rencontrez des problèmes ou avez des suggestions d'amélioration, n'hésitez pas à contribuer au projet.

**Bon développement avec Printful !** 🚀
