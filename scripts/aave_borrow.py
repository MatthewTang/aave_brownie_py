from brownie import network, config, interface
from eth_utils import address
import web3
from scripts.helpful_scripts import get_account
from scripts.get_weth import get_weth
from web3 import Web3

amount = Web3.toWei(0.1, "ether")


def main():
    account = get_account()
    erc20_address = config["networks"][network.show_active()]["weth_token"]
    if network.show_active() in ["mainnet-fork"]:
        get_weth()

    # ABI
    # Address
    lending_pool = get_lending_pool()
    # approve
    approve_erc20(amount, lending_pool.address, erc20_address, account)
    # can after approved deposit
    print("depositing...")
    tx = lending_pool.deposit(
        erc20_address, amount, account.address, 0, {"from": account}
    )
    tx.wait(1)  # wait 1 block confirmation
    print("Deposited")
    # ... how much ? getUserAccountData()
    borrowable_eth, total_debt = get_borrowable_data(lending_pool, account)
    print("let's borrow some DAI!")
    # DAI in terms of ETH
    dai_eth_price_feed = config["networks"][network.show_active()]["dai_eth_price_feed"]
    dai_eth_price = get_asset_price(dai_eth_price_feed)
    converted_dai_eth_price = Web3.fromWei(dai_eth_price, "ether")
    print(f"DAI/ ETH price is {converted_dai_eth_price}")
    amount_dai_to_borrow = (
        (1 / dai_eth_price) * borrowable_eth * 0.95
    )  # 0.95 to be safe, healther factor
    print(f"We are going to borrow {int(amount_dai_to_borrow)} DAI")
    # now we will borrow
    dai_address = config["networks"][network.show_active()]["dai_token"]
    borrow_tx = lending_pool.borrow(
        dai_address,
        Web3.toWei(amount_dai_to_borrow, "ether"),
        1,
        0,
        account.address,
        {"from": account},
    )
    borrow_tx.wait(1)
    print("we borrowed some DAI")
    get_borrowable_data(lending_pool, account)
    # repay
    repay_all(amount, lending_pool, account)
    print("you just deposited, borrowed and repayed with aave, brownie, and chainlink")


def repay_all(amount, lending_pool, account):
    approve_erc20(
        Web3.toWei(amount, "ether"),
        lending_pool,
        config["networks"][network.show_active()]["dai_token"],
        account,
    )
    repay_tx = lending_pool.repay(
        config["networks"][network.show_active()]["dai_token"],
        amount,
        1,
        account.address,
        {"from": account},
    )
    repay_tx.wait(1)
    print("repay")
    print(repay_tx)


def get_asset_price(price_feed_address):
    # ABI and address
    asset_price_feed = interface.AggregatorV3Interface(price_feed_address)
    latest_price = asset_price_feed.latestRoundData()[1]
    return float(latest_price)


def get_borrowable_data(lending_pool, account):
    print("getting borrowable data")
    user_account_data = lending_pool.getUserAccountData(
        account.address, {"from": account}
    )
    (
        total_collateral_eth,
        total_debt_eth,
        available_borrow_eth,
        current_liquidation_threshold,
        ltv,
        health_facto,
    ) = user_account_data
    print(f"user account data: {user_account_data}")
    available_borrow_eth = Web3.fromWei(available_borrow_eth, "ether")
    total_collateral_eth = Web3.fromWei(total_collateral_eth, "ether")
    total_debt_eth = Web3.fromWei(total_debt_eth, "ether")
    print(f"you have {total_collateral_eth} worth of ETH deposited.")
    print(f"you have {total_debt_eth} worth of ETH borrowed.")
    print(f"you can borrow {available_borrow_eth} worth of ETH.")
    return (float(available_borrow_eth), float(total_debt_eth))


def approve_erc20(amount, spender, erc20_address, account):
    # ABI & address also
    # we look at the eip20 standards and see what func and make our own interface
    print("Approving ERC20 token")
    erc20 = interface.IERC20(erc20_address)
    tx = erc20.approve(spender, amount, {"from": account})
    tx.wait(1)
    print("approved")
    return tx


def get_lending_pool():
    # ABI and address
    lending_pool_addresses_provider = interface.ILendingPoolAddressesProvider(
        config["networks"][network.show_active()]["lending_pool_addresses_provider"]
    )
    lending_pool_address = lending_pool_addresses_provider.getLendingPool()
    # ABI
    # address - Check!
    lending_pool = interface.ILendingPool(lending_pool_address)
    return lending_pool
