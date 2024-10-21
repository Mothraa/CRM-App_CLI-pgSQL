from my_app.services.customer_service import CustomerService


class CustomerController:
    def __init__(self, customer_service: CustomerService):
        self.customer_service = customer_service

    def list_customers(self, current_user):
        """Retrieve all customers"""
        customers = self.customer_service.get_all_customers()
        return customers

    def retrieve_customer(self, customer_id: int, current_user):
        """Retrieve a customer by ID"""
        customer = self.customer_service.get_customer_by_id(customer_id)
        return customer

    def create_customer(self, customer_data: dict, current_user):
        """create a new customer"""
        new_customer = self.customer_service.add_customer(customer_data, current_user)
        return new_customer

    def update_customer(self, customer_id: int, update_data: dict, current_user):
        """update customer's datas"""
        updated_customer = self.customer_service.update_customer(customer_id, update_data, current_user)
        return updated_customer

    def delete_customer(self, customer_id: int, current_user):
        """(soft) delete a customer"""
        self.customer_service.delete_customer(customer_id, current_user)
