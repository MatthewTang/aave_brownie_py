from web3 import Web3
from scripts.helpful_scripts import get_account
from brownie import interface, config, network


def main():
    # get_weth()
    # get_eth()
    account = get_account()
    weth_balance = get_balance_of_weth(account)
    print(f"WETH balance: {weth_balance}")


def get_weth():
    """
    Mints WETH by depositing ETH
    """
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.deposit({"from": account, "value": 0.1 * 10 ** 18})
    tx.wait(1)
    print("Received 0.1 WETH")
    return tx

    # to interact with WETH contract, we can
    # ABI
    # Address

    # or we can using the WETH interface, which we're doing above


def get_eth():
    """
    get back ETH by withdrawing WETH
    """
    account = get_account()
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    tx = weth.withdraw(Web3.toWei(0.1, "ether"), {"from": account})
    tx.wait(1)
    print("received o.1 ETH")
    return tx


def get_balance_of_weth(account):
    weth = interface.IWeth(config["networks"][network.show_active()]["weth_token"])
    weth_balance = weth.balanceOf(account.address)
    return weth_balance
