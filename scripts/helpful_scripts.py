from brownie import network, accounts, config

LOCAL_DEVELOPMENTS = ["development", "ganache", "mainnet-fork"]


def get_account(index=None, id=None):
    if index:
        return accounts[index]
    if id:
        return accounts.load(id)
    if network.show_active() in LOCAL_DEVELOPMENTS:
        return accounts[0]

    return accounts.add(config["wallets"]["from_key"])


def get_contract():
    pass
