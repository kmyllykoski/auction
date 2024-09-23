# -----------------------------------------------------------------------------
#
#       Simulation of Multiple Unit Sequential Double Auctions 
#        for lending and borrowing with Random Bids and Asks
#
# -----------------------------------------------------------------------------
import random
random.seed(42)

# parameters for random bids and asks
number_of_bids = 5
number_of_asks = 5
maturities = [5, 30, 360]  # days to maturity in ascending order
base_quantity = 100
quantity_multiply_min = 1  # for random size bids and asks
quantity_multiply_max = 10
base_interest = 10
interest_margin_min = 0    # for random interest for bids and asks
interest_margin_max = 30

def bid_string(bid):
    return f'Bid: maturity:{bid["maturity"]:4}, key:{bid["bid_key"]:2} ' \
        f'quantity:{bid["quantity"]:4}, filled:{bid["filled"]:7.2f}, ' \
        f' interest:{bid["interest"]:4.2f} interest_of_filled:{bid["interest_of_filled"]:9.2f}'

def ask_string(ask):
    return f'Ask: maturity:{ask["maturity"]:4}, key:{ask["ask_key"]:2} ' \
        f'quantity:{ask["quantity"]:4}, filled:{ask["filled"]:7.2f}, ' \
        f' interest:{ask["interest"]:4.2f} interest_of_filled:{ask["interest_of_filled"]:9.2f}, ' \
        f' i_fill_ask:{ask["i_fill_ask"]:2}, i_fill_bid:{ask["i_fill_bid"]:2}'
    
def print_all_bids(bids):
    print('All bids:')
    for b in bids:
        print(bid_string(b))

def print_all_asks(asks):
    print('All asks:')
    for a in asks:
        print(ask_string(a))

def print_all_asks_post_auction(asks):
    print('All asks:')
    for ask in asks:
        output = ask_string(ask).split('i_fill_ask:')[0]
        print(output + f' realized interest: {ask["realized_interest"]:.2f}')


# generate random bids and asks
bids = []
asks = []
filled = 0
interest_of_filled = 0  # used to sum up the interest of filled orders and for calculating 
                        # the average interest of all fills for given bid or ask
for maturity in maturities:
    for i in range(number_of_bids):
        quantity = base_quantity * int(random.uniform(quantity_multiply_min, quantity_multiply_max))
        interest = base_interest + int(random.uniform(interest_margin_min, interest_margin_max))
        bids.append({
            'maturity': maturity,
            'bid_key':i, 
            'quantity':  quantity, 
            'filled': filled,
            'interest': interest, 
            'interest_of_filled': interest_of_filled
            })

    for i in range(number_of_asks):
        quantity = base_quantity * int(random.uniform(quantity_multiply_min, quantity_multiply_max))
        interest = base_interest + int(random.uniform(interest_margin_min, interest_margin_max))
        asks.append({
            'maturity': maturity,
            'ask_key':i,
            'quantity': quantity,
            'filled': filled,
            'interest': interest,
            'interest_of_filled': interest_of_filled,
            'i_fill_ask': 'NA',  # stores index of fillable ask
            'i_fill_bid': 'NA'   # stores index of fillable bid
            })

print('Random bids and asks in before auctions')
print_all_bids(bids)
print_all_asks(asks)

auction_bids_total = 0     # total bid quantity in the auction
auction_asks_total = 0  
bids_post_auction = []     # all of bids after auction
asks_post_auction = []  
auction_tvl_bids = 0       # total value locked after auction
auction_tvl_asks = 0
auction_interest_bids = 0  # interest of filled bids after auction
auction_interest_asks = 0

# loop maturities in reverse order from largest to smallest
for maturity in reversed(maturities):
    print('=' * 80)
    print(f'Processing maturity: {maturity}')

    # get bids and asks to be matched for the current maturity 
    bids_with_this_maturity = [bid for bid in bids if bid['maturity'] == maturity]
    asks_with_this_maturity = [ask for ask in asks if ask['maturity'] == maturity]
    
    # sort bids by interest in ascending order
    bids_with_this_maturity.sort(key = lambda bid: bid['interest'])
    # sort asks by interest in descending order
    asks_with_this_maturity.sort(key = lambda ask: -ask['interest'])
    
    # loop bids_with_this_maturity
    for idx_bid, bid in enumerate(bids_with_this_maturity):
        print('-' * 80)
        print(bid_string(bid))
        unfilled_bid_amount = bid['quantity'] - bid['filled']
        bid_interest = bid['interest']
        # is the bid still unfilled?
        if unfilled_bid_amount > 0:
            # loop asks_with_this_maturity
            asks_fillable_with_this_bid = []
            for idx_ask, ask in enumerate(asks_with_this_maturity):
                print('   ' + ask_string(ask), end='')
                # is the ask still unfilled?
                if ask['quantity'] > ask['filled']:
                    if ask['interest'] >= bid['interest']:
                        # if the interest of ask is higher or equal to that of bid, 
                        # then append this bid to fillable_with_this_bid
                        print(' - fillable ok')
                        # save the index of this matching bid and ask
                        ask['i_fill_bid'] = idx_bid
                        ask['i_fill_ask'] = idx_ask
                        asks_fillable_with_this_bid.append(ask)
                    else:
                        # if the interest of ask was lower than bid,
                        #  then later bids in the loop can't match
                        print(' - interest too low')
                        break
                else:
                    print(' - already filled')

            print('***all asks validated for this bid')        
            # if there is no ask that can be filled with this bid, then continue
            if len(asks_fillable_with_this_bid) == 0:
                print('no ask that can be filled with this bid -> continue to next bid')
                if idx_bid < len(bids_with_this_maturity) -1:
                    print('\n' + f'next bid for maturity {maturity}')
                continue
            
            # get sum of unfilled quantity of fillable_with_this_bid
            total_unfilled_asks = sum(
                [ask['quantity'] - ask['filled'] for ask in asks_fillable_with_this_bid])
            print(f'unfilled bid amount: {unfilled_bid_amount:7.2f} ' \
                f'for unfilled ask amount: {total_unfilled_asks:7.2f}')

            # if total unfilled is smaller or equal to unfilled bid quantity, 
            # then fill all the valid asks with this bid
            if total_unfilled_asks <= unfilled_bid_amount:
                print('fills:')
                for ask in asks_fillable_with_this_bid:
                    # print(ask_string(ask))
                    # update filled amount in bids and asks with unfilled_ask
                    unfilled_ask = ask['quantity'] - ask['filled']
                    asks_with_this_maturity[ask['i_fill_ask']]['filled'] += unfilled_ask 
                    bids_with_this_maturity[ask['i_fill_bid']]['filled'] += unfilled_ask
                    
                    # update interest of this fill in bids and asks
                    interest_of_this_fill = bid_interest * unfilled_ask * (maturity / 360) / 100
                    asks_with_this_maturity[ask['i_fill_ask']]['interest_of_filled'] += interest_of_this_fill 
                    bids_with_this_maturity[ask['i_fill_bid']]['interest_of_filled'] += interest_of_this_fill
                    print(f'   FILL FULLY     ask key {ask['ask_key']:2},  interest: {bid_interest:4.2f} ' \
                        f'fill: {unfilled_ask:7.2f} interest amount: {interest_of_this_fill:4.2f}')
            else:
                # get the ratio for filling asks 
                ratio = unfilled_bid_amount / total_unfilled_asks
                print(f'asks can be filled with ratio: {ratio:5.4f}')
                print('fills:')
                filled_total = 0
                for ask in asks_fillable_with_this_bid:
                    # update filled amount in bids and asks with unfilled_ask
                    unfilled_ask = ask['quantity'] - ask['filled']
                    fillable_amount = unfilled_ask * ratio
                    # handle rounding errors so that bid amount is not exceeded
                    if fillable_amount + filled_total > unfilled_bid_amount:
                        fillable_amount = unfilled_bid_amount - filled_total
                    filled_total += fillable_amount
                    
                    asks_with_this_maturity[ask['i_fill_ask']]['filled'] += fillable_amount 
                    bids_with_this_maturity[ask['i_fill_bid']]['filled'] += fillable_amount
                    
                    interest_of_this_fill = bid_interest * fillable_amount * (maturity / 360) / 100
                    asks_with_this_maturity[ask['i_fill_ask']]['interest_of_filled'] += interest_of_this_fill 
                    bids_with_this_maturity[ask['i_fill_bid']]['interest_of_filled'] += interest_of_this_fill
                    
                    print(f'   FILL PARTIAL   ask key: {ask['ask_key']:2}, interest: {bid_interest:4.2f} ' \
                        f'fill: {fillable_amount:7.2f} interest amount: {interest_of_this_fill:4.2f}')
                                      
            print('updated asks:')
            for ask in asks_with_this_maturity:
                print(ask_string(ask))
                ask['i_fill_bid'], ask['i_fill_ask'] = 'NA', 'NA'
            print('updated bids:')
            for bid in bids_with_this_maturity:
                print(bid_string(bid))
        else:
            print('this bid is already filled')
            continue
        if idx_bid < len(bids_with_this_maturity) -1:
            print('\n' + f'next bid for maturity {maturity}')
        
    print(f'*** ALL BIDS WITH MATURITY {maturity} PROCESSED ***')

    print('updated bids:')
    for bid in bids_with_this_maturity:
        if bid['filled'] > 0:
            realized_interest = bid['interest_of_filled'] / bid['filled'] * (360 / maturity) * 100
        else:
            realized_interest = 0 
        print(bid_string(bid), end='')
        print(f' realized interest: {realized_interest:4.2f}')
        auction_bids_total += bid['quantity']
        auction_tvl_bids += bid['filled']
        auction_interest_bids += bid['interest_of_filled']
        bids_post_auction.append(bid)

    print('updated asks:')
    for ask in asks_with_this_maturity:
        if ask['filled'] > 0:
            realized_interest = ask['interest_of_filled'] / ask['filled'] * (360 / maturity) * 100
        else:
            realized_interest = 0 
        print(ask_string(ask), end='')
        print(f' realized interest: {realized_interest:4.2f}')
        
        auction_asks_total += ask['quantity']
        auction_tvl_asks += ask['filled']
        auction_interest_asks += ask['interest_of_filled']
        ask['i_fill_bid'], ask['i_fill_ask'] = 'NA', 'NA'
        ask['realized_interest'] = realized_interest
        asks_post_auction.append(ask)
                        
print('********* ALL BIDS PROCESSED *********')

print('********* BIDS AND ASKS POST AUCTION *********')
print_all_bids(bids_post_auction)
print_all_asks_post_auction(asks_post_auction)

print('\n********* AUCTION RESULTS ***********\n')
print(f'value of all bids: {auction_bids_total}')
print(f'tvl of all bids: {auction_tvl_bids:.2f} ' \
    f'({auction_tvl_bids / auction_bids_total * 100:.2f}% of bids filled)')
print(f'interest of all bids: {auction_interest_bids:.2f}')
print()
print(f'value of all asks: {auction_asks_total}')
print(f'tvl of all asks: {auction_tvl_asks:.2f} ' \
    f'({auction_tvl_asks / auction_asks_total * 100:.2f}% of asks filled)')
print(f'interest of all asks: {auction_interest_asks:.2f}')

print('\n========== DONE ==========')


            

            




