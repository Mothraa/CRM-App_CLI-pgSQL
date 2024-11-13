from my_app.decorators import log_user_actions
from my_app.models import Customer
from my_app.schemas.customer_schemas import CustomerAddSchema, CustomerUpdateSchema
from my_app.exceptions import CustomerNotFoundError
from my_app.utils.encryption_utils import encrypt, decrypt


class CustomerService:
    def __init__(self, session, customer_repository):
        """
        Services to create and manage customer data.
        param :
            session => the SQLAlchemy session to manage the database
            customer_repository => repository to manage customer data/sqlalchemy operations
        """
        self.session = session
        self.customer_repository = customer_repository

    def get_by_id(self, customer_id: int):
        """Retrieve a customer by his ID"""
        customer = self.customer_repository.get_by_id(customer_id)
        if not customer:
            raise CustomerNotFoundError(f"No customer with ID: {customer_id}")

        # dechiffrement des données
        if customer.company_name:
            customer.company_name = decrypt(customer.company_name)
        if customer.full_name:
            customer.full_name = decrypt(customer.full_name)
        if customer.email:
            customer.email = decrypt(customer.email)
        if customer.phone_number:
            customer.phone_number = decrypt(customer.phone_number)
        return customer

    def get_all(self):
        """Retrieve all customers"""
        customers = self.customer_repository.get_all()
        for customer in customers:
            if customer.company_name:
                customer.company_name = decrypt(customer.company_name)
            if customer.full_name:
                customer.full_name = decrypt(customer.full_name)
            if customer.email:
                customer.email = decrypt(customer.email)
            if customer.phone_number:
                customer.phone_number = decrypt(customer.phone_number)
        return customers

    @log_user_actions("Ajout d'un client")
    def add(self, customer_data: dict):
        """Method to add a new customer"""
        # on valide les données d'entrée avec pydantic
        customer_add = CustomerAddSchema(**customer_data)
        # on converti les données pydantic en dict
        customer_add_dict = customer_add.model_dump()

        # chiffrement des données
        if 'company_name' in customer_add_dict:
            customer_add_dict['company_name'] = encrypt(customer_add_dict['company_name'])
        if 'full_name' in customer_add_dict:
            customer_add_dict['full_name'] = encrypt(customer_add_dict['full_name'])
        if 'email' in customer_add_dict:
            customer_add_dict['email'] = encrypt(customer_add_dict['email'])
        if 'phone_number' in customer_add_dict:
            customer_add_dict['phone_number'] = encrypt(customer_add_dict['phone_number'])

        # on créé le nouveau Customer via le repository
        # TODO : passer un dict pour éviter une dépendance au modèle
        new_customer = self.customer_repository.add(Customer(**customer_add_dict))
        return new_customer

    @log_user_actions("Modification d'un client")
    def update(self, customer_id: int, update_data: dict):
        """Method to update an existing customer."""
        # on valide les données d'entrée avec pydantic
        customer_update = CustomerUpdateSchema(**update_data)

        # on récupère les données a mettre à jour
        customer_to_update = self.customer_repository.get_by_id(customer_id)
        if not customer_to_update:
            raise CustomerNotFoundError(f"No customer with ID: {customer_id}")

        data_to_update_dict = customer_update.model_dump(exclude_unset=True)
        # chiffrement des données
        if 'company_name' in data_to_update_dict:
            data_to_update_dict['company_name'] = encrypt(data_to_update_dict['company_name'])
        if 'full_name' in data_to_update_dict:
            data_to_update_dict['full_name'] = encrypt(data_to_update_dict['full_name'])
        if 'email' in data_to_update_dict:
            data_to_update_dict['email'] = encrypt(data_to_update_dict['email'])
        if 'phone_number' in data_to_update_dict:
            data_to_update_dict['phone_number'] = encrypt(data_to_update_dict['phone_number'])

        # # on applique la mise à jour des attributs
        for key, value in data_to_update_dict.items():
            setattr(customer_to_update, key, value)
        # sauvegarde via le repository
        updated_customer = self.customer_repository.update(customer_to_update, data_to_update_dict)
        return updated_customer

    @log_user_actions("Suppression d'un client")
    def delete(self, customer_id: int):
        """Method to delete a customer (soft delete)."""
        # on récupère le Customer à supprimer
        customer_to_delete = self.customer_repository.get_by_id(customer_id)
        if not customer_to_delete:
            raise CustomerNotFoundError(f"No customer with ID: {customer_id}")

        # on fait le (soft) delete via le repository
        self.customer_repository.delete(customer_to_delete)
        # on ne retourne rien, par cohérence avec le repository et pour ne pas exposer les données
