from librouteros import connect

def create_pppoe_client(router, username, password, pool=None, profile=None):
    try:
        # Connect to the router
        api = connect(username=router.username, password=router.password, host=router.ip_address)

        # Prepare the PPPoE client data
        pppoe_data = {
            'name': username,
            'password': password,
            'service': 'pppoe',
        }
        if pool:
            pppoe_data['remote-address'] = pool
        if profile:
            pppoe_data['profile'] = profile

        # Add the PPPoE client
        ppp = api.path('ppp', 'secret')
        ppp.add(**pppoe_data)

        return True
    except Exception as e:
        print(f"Error creating PPPoE client on Mikrotik: {str(e)}")
        return False