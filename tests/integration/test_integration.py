import pytest
from click.testing import CliRunner
from my_app.cli.main_cli import cli
from my_app.dependencies import (init_user_controller,
                                 init_main_controller,
                                 init_customer_controller,
                                 init_contract_controller,
                                 init_event_controller
                                 )
from my_app.models import User, Contract, Event, Customer


@pytest.mark.integration
def test_complete_scenario(db_session):
    runner = CliRunner()

    # on init les controller

    main_controller = init_main_controller(db_session)
    user_controller = init_user_controller(db_session)
    customer_controller = init_customer_controller(db_session)
    contract_controller = init_contract_controller(db_session)
    event_controller = init_event_controller(db_session)

    # on les ajoute au context de l"app
    app_context = {
        "session": db_session,
        "user_controller": user_controller,
        "main_controller": main_controller,
        "customer_controller": customer_controller,
        "contract_controller": contract_controller,
        "event_controller": event_controller,
    }

    # Init des variables de test
    user = None
    customer = None
    contract = None
    event = None

    with runner.isolated_filesystem():
        try:
            # connexion en tant qu"admin
            # TODO : changer de compte entre chaque action.
            login_result = runner.invoke(
                cli, ["login", "admin@test.com"],
                input="Super_passwordQuiR3spectLéContraintes!!\n",
                obj=app_context
            )
            assert login_result.exit_code == 0
            assert "Utilisateur admin@test.com authentifié." in login_result.output

            # ajouter un utilisateur (également admin)
            user_result = runner.invoke(
                cli, ["user", "add", "user@test.com", "password123!", "Michel", "Letesteur", "admin"],
                obj=app_context
            )
            assert user_result.exit_code == 0
            assert "User user@test.com added!" in user_result.output

            # on vérifie que l"utilisateur a bien été créé en base
            user = db_session.query(User).filter_by(email="user@test.com").first()
            assert user is not None

            # création d"un client (customer)
            customer_result = runner.invoke(
                cli, ["customer", "add", "Compagnie Test", "Client Test"],
                obj=app_context
            )
            assert customer_result.exit_code == 0
            assert "Customer added!" in customer_result.output

            # on vérifie que le client a bien été créé en base
            customer = db_session.query(Customer).filter_by(company_name="Compagnie Test").first()
            assert customer is not None

            # création d"un contrat pour ce client
            contract_result = runner.invoke(
                cli, ["contract", "add", str(customer.id), str(user.id),
                      "--total_amount", "1000", "--status", "pending"
                      ],
                obj=app_context
            )
            assert contract_result.exit_code == 0
            assert "Contract added!" in contract_result.output

            # on vérifie que le contrat a bien été créé en base
            contract = db_session.query(Contract).filter_by(customer_id=customer.id).first()
            assert contract is not None

            # modification du statut du contrat en signé
            update_contract_status_result = runner.invoke(
                cli, ["contract", "update", str(contract.id), "--status", "signed"],
                obj=app_context
            )
            assert update_contract_status_result.exit_code == 0
            assert "Contract updated!" in update_contract_status_result.output
            db_session.commit()
            # création d'un événement (event) pour ce contrat
            event_result = runner.invoke(
                cli, ["event", "add", "--contract_id", str(contract.id),
                      "--name", "Test Event", "--location", "Test Location"
                      ],
                obj=app_context
            )
            assert event_result.exit_code == 0
            assert "Event 'Test Event' added!" in event_result.output
            # on vérifie que l'événement a été créé dans la base de données
            event = db_session.query(Event).filter_by(contract_id=contract.id).first()
            assert event is not None

            # déconnexion
            logout_result = runner.invoke(cli, ["logout"], obj=app_context)
            assert logout_result.exit_code == 0
            assert "Déconnexion réussie" in logout_result.output
        finally:
            # Nettoyage des données
            # (sans passer par le controller sinon soft delete uniquement)
            if event:
                db_session.delete(event)
            if contract:
                db_session.delete(contract)
            if customer:
                db_session.delete(customer)
            if user:
                db_session.delete(user)
            db_session.commit()
