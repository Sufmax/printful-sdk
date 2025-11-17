import requests
from typing import Optional, Dict, Any, List, Union


class PrintfulSDK:
    """SDK Python pour l'API Printful"""
    
    def __init__(self, api_key: Optional[str] = None, store_id: Optional[int] = None):
        """
        Initialise le client SDK Printful
        
        Args:
            api_key: Clé API ou token OAuth Printful
            store_id: ID de la boutique (requis pour les tokens Account-level)
        """
        self.base_url = "https://api.printful.com"
        self.api_key = api_key
        self.store_id = store_id
        self.session = requests.Session()
        self._update_headers()
    
    def set_api_key(self, api_key: str) -> None:
        """Définit ou met à jour la clé API"""
        self.api_key = api_key
        self._update_headers()
    
    def set_store_id(self, store_id: int) -> None:
        """Définit ou met à jour l'ID de la boutique pour les tokens Account-level"""
        self.store_id = store_id
        self._update_headers()
    
    def _update_headers(self) -> None:
        """Met à jour les headers de session"""
        if self.api_key:
            self.session.headers.update({
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            })
        if self.store_id:
            self.session.headers.update({
                "X-PF-Store-Id": str(self.store_id)
            })
    
    def _process_id_param(self, id_or_external_id: Union[int, str]) -> str:
        """Convertit automatiquement les external_ids avec le préfixe @"""
        if isinstance(id_or_external_id, int):
            return str(id_or_external_id)
        elif isinstance(id_or_external_id, str):
            if not id_or_external_id.isdigit() and not id_or_external_id.startswith("@"):
                return f"@{id_or_external_id}"
            return id_or_external_id
        return str(id_or_external_id)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """Effectue une requête HTTP et gère les erreurs"""
        url = f"{self.base_url}{endpoint}"
        response = self.session.request(method, url, **kwargs)
        response.raise_for_status()
        return response.json()
    
    # OAuth & Permissions
    def get_oauth_scopes(self) -> Dict[str, Any]:
        """Récupère la liste des scopes associés au token d'authentification"""
        return self._make_request("GET", "/oauth/scopes")
    
    # Catalogue Produits
    def get_products(self, offset: int = 0, limit: int = 20, category_id: Optional[Union[int, List[int]]] = None) -> Dict[str, Any]:
        """
        Récupère la liste des produits du catalogue
        
        Args:
            offset: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments à retourner
            category_id: ID(s) de catégorie pour filtrer
        """
        params = {"offset": offset, "limit": limit}
        if category_id:
            if isinstance(category_id, list):
                params["category_id"] = ",".join(map(str, category_id))
            else:
                params["category_id"] = str(category_id)
        return self._make_request("GET", "/products", params=params)
    
    def get_product(self, product_id: int) -> Dict[str, Any]:
        """Récupère les détails d'un produit spécifique"""
        return self._make_request("GET", f"/products/{product_id}")
    
    def get_product_variant(self, variant_id: int) -> Dict[str, Any]:
        """Récupère les détails d'une variante spécifique"""
        return self._make_request("GET", f"/products/variant/{variant_id}")
    
    def get_product_sizes(self, product_id: int) -> Dict[str, Any]:
        """Récupère les guides des tailles pour un produit"""
        return self._make_request("GET", f"/products/{product_id}/sizes")
    
    # Catégories
    def get_categories(self) -> Dict[str, Any]:
        """Récupère la liste de toutes les catégories de produits"""
        return self._make_request("GET", "/categories")
    
    def get_category(self, category_id: int) -> Dict[str, Any]:
        """Récupère les détails d'une catégorie spécifique"""
        return self._make_request("GET", f"/categories/{category_id}")
    
    # Store Products (Produits synchronisés)
    def create_store_product(self, sync_product: Dict[str, Any], sync_variants: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Crée un nouveau produit synchronisé dans la boutique
        
        Args:
            sync_product: Données du produit (name, external_id optionnel, etc.)
            sync_variants: Liste des variantes avec variant_id, retail_price, files, etc.
        """
        data = {
            "sync_product": sync_product,
            "sync_variants": sync_variants
        }
        return self._make_request("POST", "/store/products", json=data)
    
    def get_store_products(self, offset: int = 0, limit: int = 20, status: Optional[str] = None, 
                          search: Optional[str] = None, store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Récupère la liste des produits synchronisés
        
        Args:
            offset: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments à retourner
            status: Filtrer par statut (all, synced, unsynced, ignored, imported, discontinued, out_of_stock)
            search: Terme de recherche
            store_id: Override du store_id global
        """
        params = {"offset": offset, "limit": limit}
        if status:
            params["status"] = status
        if search:
            params["search"] = search
        
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        
        return self._make_request("GET", "/store/products", params=params, headers=headers if headers else None)
    
    def get_store_product(self, id_or_external_id: Union[int, str], store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Récupère les détails d'un produit synchronisé
        
        Args:
            id_or_external_id: ID numérique ou external_id du produit
            store_id: Override du store_id global
        """
        product_id = self._process_id_param(id_or_external_id)
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        return self._make_request("GET", f"/store/products/{product_id}", headers=headers if headers else None)
    
    def update_store_product(self, id_or_external_id: Union[int, str], 
                            sync_product: Optional[Dict[str, Any]] = None,
                            sync_variants: Optional[List[Dict[str, Any]]] = None,
                            store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Met à jour un produit synchronisé existant
        
        Args:
            id_or_external_id: ID numérique ou external_id du produit
            sync_product: Données du produit à mettre à jour
            sync_variants: Variantes à mettre à jour
            store_id: Override du store_id global
        """
        product_id = self._process_id_param(id_or_external_id)
        data = {}
        if sync_product:
            data["sync_product"] = sync_product
        if sync_variants:
            data["sync_variants"] = sync_variants
        
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        
        return self._make_request("PUT", f"/store/products/{product_id}", json=data, headers=headers if headers else None)
    
    def delete_store_product(self, id_or_external_id: Union[int, str], store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Supprime un produit synchronisé
        
        Args:
            id_or_external_id: ID numérique ou external_id du produit
            store_id: Override du store_id global
        """
        product_id = self._process_id_param(id_or_external_id)
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        return self._make_request("DELETE", f"/store/products/{product_id}", headers=headers if headers else None)
    
    # Store Variants
    def get_store_variant(self, id_or_external_id: Union[int, str], store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Récupère les détails d'une variante synchronisée
        
        Args:
            id_or_external_id: ID numérique ou external_id de la variante
            store_id: Override du store_id global
        """
        variant_id = self._process_id_param(id_or_external_id)
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        return self._make_request("GET", f"/store/variants/{variant_id}", headers=headers if headers else None)
    
    def create_store_variant(self, sync_product_id: Union[int, str], variant_data: Dict[str, Any], 
                            store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Crée une nouvelle variante pour un produit synchronisé
        
        Args:
            sync_product_id: ID du produit synchronisé parent
            variant_data: Données de la variante (variant_id, retail_price, files, etc.)
            store_id: Override du store_id global
        """
        product_id = self._process_id_param(sync_product_id)
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        return self._make_request("POST", f"/store/products/{product_id}/variants", json=variant_data, 
                                 headers=headers if headers else None)
    
    def update_store_variant(self, id_or_external_id: Union[int, str], variant_data: Dict[str, Any],
                            store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Met à jour une variante synchronisée
        
        Args:
            id_or_external_id: ID numérique ou external_id de la variante
            variant_data: Données à mettre à jour
            store_id: Override du store_id global
        """
        variant_id = self._process_id_param(id_or_external_id)
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        return self._make_request("PUT", f"/store/variants/{variant_id}", json=variant_data, 
                                 headers=headers if headers else None)
    
    def delete_store_variant(self, id_or_external_id: Union[int, str], store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Supprime une variante synchronisée
        
        Args:
            id_or_external_id: ID numérique ou external_id de la variante
            store_id: Override du store_id global
        """
        variant_id = self._process_id_param(id_or_external_id)
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        return self._make_request("DELETE", f"/store/variants/{variant_id}", headers=headers if headers else None)
    
    # Commandes (OPÉRATIONS SENSIBLES)
    def create_order(self, recipient: Dict[str, Any], items: List[Dict[str, Any]], 
                    shipping: Optional[str] = None, external_id: Optional[str] = None,
                    packing_slip: Optional[Dict[str, Any]] = None, confirm: bool = False,
                    update_existing: bool = False, store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Crée une nouvelle commande (OPÉRATION SENSIBLE - désactivée par sécurité)
        
        Args:
            recipient: Informations du destinataire
            items: Liste des articles à commander
            shipping: Code du transporteur
            external_id: ID externe optionnel
            packing_slip: Configuration du bordereau
            confirm: Si True, confirme automatiquement la commande
            update_existing: Si True, met à jour une commande existante avec le même external_id
            store_id: Override du store_id global
        """
        print("⚠️ ATTENTION: create_order() est une opération financière sensible - désactivée par sécurité")
        print("   Pour activer cette fonction, décommentez la ligne de requête dans le code source")
        
        data = {
            "recipient": recipient,
            "items": items
        }
        if shipping:
            data["shipping"] = shipping
        if external_id:
            data["external_id"] = external_id
        if packing_slip:
            data["packing_slip"] = packing_slip
        if confirm:
            data["confirm"] = confirm
        if update_existing:
            data["update_existing"] = update_existing
        
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        
        # response = self._make_request("POST", "/orders", json=data, headers=headers if headers else None)
        return {"status": "mock_success", "message": "Operation deactivated for safety.", "mock_order_id": "12345"}
    
    def get_orders(self, offset: int = 0, limit: int = 20, status: Optional[str] = None,
                  store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Récupère la liste des commandes
        
        Args:
            offset: Nombre d'éléments à sauter
            limit: Nombre maximum d'éléments à retourner
            status: Filtrer par statut de commande
            store_id: Override du store_id global
        """
        params = {"offset": offset, "limit": limit}
        if status:
            params["status"] = status
        
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        
        return self._make_request("GET", "/orders", params=params, headers=headers if headers else None)
    
    def get_order(self, id_or_external_id: Union[int, str], store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Récupère les détails d'une commande
        
        Args:
            id_or_external_id: ID numérique ou external_id de la commande
            store_id: Override du store_id global
        """
        order_id = self._process_id_param(id_or_external_id)
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        return self._make_request("GET", f"/orders/{order_id}", headers=headers if headers else None)
    
    def update_order(self, id_or_external_id: Union[int, str], order_data: Dict[str, Any],
                    store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Met à jour une commande non soumise
        
        Args:
            id_or_external_id: ID numérique ou external_id de la commande
            order_data: Données à mettre à jour
            store_id: Override du store_id global
        """
        order_id = self._process_id_param(id_or_external_id)
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        return self._make_request("PUT", f"/orders/{order_id}", json=order_data, headers=headers if headers else None)
    
    def confirm_order(self, id_or_external_id: Union[int, str], store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Confirme une commande brouillon (OPÉRATION SENSIBLE - désactivée par sécurité)
        
        Args:
            id_or_external_id: ID numérique ou external_id de la commande
            store_id: Override du store_id global
        """
        print("⚠️ ATTENTION: confirm_order() déclenche facturation et production - désactivée par sécurité")
        print("   Pour activer cette fonction, décommentez la ligne de requête dans le code source")
        
        order_id = self._process_id_param(id_or_external_id)
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        
        # response = self._make_request("POST", f"/orders/{order_id}/confirm", headers=headers if headers else None)
        return {"status": "mock_success", "message": "Operation deactivated for safety.", "mock_confirmed": True}
    
    def cancel_order(self, id_or_external_id: Union[int, str], store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Annule une commande (OPÉRATION SENSIBLE - désactivée par sécurité)
        
        Args:
            id_or_external_id: ID numérique ou external_id de la commande
            store_id: Override du store_id global
        """
        print("⚠️ ATTENTION: cancel_order() peut déclencher un remboursement - désactivée par sécurité")
        print("   Pour activer cette fonction, décommentez la ligne de requête dans le code source")
        
        order_id = self._process_id_param(id_or_external_id)
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        
        # response = self._make_request("DELETE", f"/orders/{order_id}", headers=headers if headers else None)
        return {"status": "mock_success", "message": "Operation deactivated for safety.", "mock_canceled": True}
    
    def estimate_order_costs(self, recipient: Dict[str, Any], items: List[Dict[str, Any]],
                           shipping: Optional[str] = None, store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Calcule les coûts estimés d'une commande sans la créer
        
        Args:
            recipient: Informations du destinataire
            items: Liste des articles
            shipping: Code du transporteur
            store_id: Override du store_id global
        """
        data = {
            "recipient": recipient,
            "items": items
        }
        if shipping:
            data["shipping"] = shipping
        
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        
        return self._make_request("POST", "/orders/estimate-costs", json=data, headers=headers if headers else None)
    
    # Files
    def add_file(self, url: str, type: Optional[str] = None, filename: Optional[str] = None,
                store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Ajoute un fichier à la bibliothèque via URL
        
        Args:
            url: URL du fichier à télécharger
            type: Type de fichier (default, preview, etc.)
            filename: Nom du fichier optionnel
            store_id: Override du store_id global
        """
        data = {"url": url}
        if type:
            data["type"] = type
        if filename:
            data["filename"] = filename
        
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        
        return self._make_request("POST", "/files", json=data, headers=headers if headers else None)
    
    def get_file(self, file_id: int, store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Récupère les informations d'un fichier
        
        Args:
            file_id: ID du fichier
            store_id: Override du store_id global
        """
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        return self._make_request("GET", f"/files/{file_id}", headers=headers if headers else None)
    
    # Mockup Generator
    def get_mockup_printfiles(self, product_id: int) -> Dict[str, Any]:
        """Récupère les zones d'impression disponibles pour un produit"""
        return self._make_request("GET", f"/mockup-generator/printfiles/{product_id}")
    
    def create_mockup_task(self, product_id: int, variant_ids: List[int], files: List[Dict[str, Any]],
                          format: str = "jpg", width: Optional[int] = None,
                          product_options: Optional[Dict[str, Any]] = None,
                          store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Crée une tâche de génération de mockup
        
        Args:
            product_id: ID du produit
            variant_ids: Liste des IDs de variantes
            files: Liste des fichiers à appliquer
            format: Format de sortie (jpg, png)
            width: Largeur en pixels
            product_options: Options additionnelles
            store_id: Override du store_id global
        """
        data = {
            "variant_ids": variant_ids,
            "files": files,
            "format": format
        }
        if width:
            data["width"] = width
        if product_options:
            data["product_options"] = product_options
        
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        
        return self._make_request("POST", f"/mockup-generator/create-task/{product_id}", 
                                 json=data, headers=headers if headers else None)
    
    def get_mockup_task_result(self, task_key: str, store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Récupère le résultat d'une tâche de mockup
        
        Args:
            task_key: Clé de la tâche retournée lors de la création
            store_id: Override du store_id global
        """
        params = {"task_key": task_key}
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        return self._make_request("GET", "/mockup-generator/task", params=params, headers=headers if headers else None)
    
    def get_mockup_templates(self, product_id: int) -> Dict[str, Any]:
        """Récupère les templates de mockup disponibles pour un produit"""
        return self._make_request("GET", f"/mockup-generator/templates/{product_id}")
    
    # Shipping
    def calculate_shipping_rates(self, recipient: Dict[str, Any], items: List[Dict[str, Any]],
                                currency: Optional[str] = None, locale: Optional[str] = None,
                                store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Calcule les tarifs d'expédition disponibles
        
        Args:
            recipient: Informations du destinataire
            items: Liste des articles
            currency: Code de devise (USD, EUR, etc.)
            locale: Code de locale pour la traduction
            store_id: Override du store_id global
        """
        data = {
            "recipient": recipient,
            "items": items
        }
        if currency:
            data["currency"] = currency
        if locale:
            data["locale"] = locale
        
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        
        return self._make_request("POST", "/shipping/rates", json=data, headers=headers if headers else None)
    
    # Stores
    def get_stores(self) -> Dict[str, Any]:
        """Récupère la liste des boutiques associées au compte"""
        return self._make_request("GET", "/stores")
    
    def get_store(self, store_id: int) -> Dict[str, Any]:
        """
        Récupère les détails d'une boutique spécifique
        
        Args:
            store_id: ID de la boutique
        """
        return self._make_request("GET", f"/stores/{store_id}")
    
    # Webhooks
    def get_webhooks(self, store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Récupère la configuration actuelle des webhooks
        
        Args:
            store_id: Override du store_id global
        """
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        return self._make_request("GET", "/webhooks", headers=headers if headers else None)
    
    def set_webhooks(self, url: str, events: List[str], types: Optional[List[str]] = None,
                    store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Configure ou met à jour les webhooks
        
        Args:
            url: URL de destination des webhooks
            events: Liste des événements à écouter
            types: Types optionnels de webhooks
            store_id: Override du store_id global
        """
        data = {
            "url": url,
            "events": events
        }
        if types:
            data["types"] = types
        
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        
        return self._make_request("POST", "/webhooks", json=data, headers=headers if headers else None)
    
    def delete_webhooks(self, store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Supprime la configuration des webhooks
        
        Args:
            store_id: Override du store_id global
        """
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        return self._make_request("DELETE", "/webhooks", headers=headers if headers else None)
    
    # Reports
    def get_statistics(self, report_type: str, date_from: str, date_to: str,
                       currency: Optional[str] = None, store_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Récupère des rapports statistiques
        
        Args:
            report_type: Type de rapport (orders, profit, etc.)
            date_from: Date de début (YYYY-MM-DD)
            date_to: Date de fin (YYYY-MM-DD)
            currency: Code de devise
            store_id: Override du store_id global
        """
        params = {
            "report_type": report_type,
            "date_from": date_from,
            "date_to": date_to
        }
        if currency:
            params["currency"] = currency
        
        headers = {}
        if store_id:
            headers["X-PF-Store-Id"] = str(store_id)
        
        return self._make_request("GET", "/reports/statistics", params=params, headers=headers if headers else None)
