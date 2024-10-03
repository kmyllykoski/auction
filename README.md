# Decentralized Lending with Sequential Double Auctions
 
# Abstract
By leveraging a decentralized blockchain protocol infrastructure lenders and borrowers can use an periodically run auction-based market to bid and ask loans of any token, collateral and maturity combination the decentralized autonomous organization (DAO) has voted to accept, at any size of loan by giving bids and asks according to their individual preferences on loan amount, maturity and interest.
 
# Rules of sequential double auctions for lending and borrowing
Auction bids and asks are matched periodically with intervals described as “Call markets”.
One Auction is held for each token, collateral, and maturity combination the DAO has voted to accept for auction lending. DAO will also decide the minimum level of collateral as a health factor for the token and maturity pairs.
Auction opens for bids and asks at a given time and continues until auction end time. To prevent last minute bid sniping the auction will end only if no bids or asks are made or withdrawn during a fixed amount of time before auction end time, otherwise soft ending is used, and the auction end time will be postponed with fixed time to give participants time to react to last minute bids or asks or them being withdrawn.

*Bids*

Bids in an auction with the given token and maturity are made with a deposit of liquidity together with the demand of interest the bidder is willing to accept (lending amount and interest pair) into the smart contract running the auction. Lender’s deposit in the smart contract at the time of the ending of the auction makes the bid binding.

*Asks*

Asks are made with a deposit of collateral together with the interest borrower is willing to accept (collateral amount and interest pair) into the auction pool. When a new auction is created, minimum collateral requirement is calculated with market data on collateral token value. The collateral amount of the ask is divided with a fixed health factor to calculate the amount of token to be borrowed with the ask (borrowing amount). Borrower’s deposit of collateral at the time of the ending of the auction makes the ask binding at the closing time of the auction.
Valid interest rate of both bids and asks can be restricted to be at fixed intervals, for example 0.1 %.

Bids and asks can be withdrawn from the auction contract any time during the auction. Withdrawal of bids or asks will be charged with a withdrawal fee as a combination of a fixed fee and a percentage of the withdrawn lending or borrowing amount. Withdraw fees are necessary firstly to prevent attack with unserious small bids and asks, and secondly to prevent strategically placed large bids with low interest or asks with high interest that would be withdrawn at the last moment before auction end to discourage competitive bids or asks from participating in the auction.  

After the auction has come to an end and bids and asks have been cleared, auction deposits of unsuccessful bids and asks are returned after deducting a participation fee to discourage unserious bids and asks.  
 
# Auction clearing mechanism
Auction clearing is done by ordering bids in ascending order by interest and asks ordered in descending order by interest. If there is a tie with the same interest the time of placing the bid or ask is used to determine order of clearing.
Clearing is done by taking ordered bids one by one starting from the bid with lowest interest and dividing the bid to all the asks that have higher or equal interest than the bid interest in proportion of the ask amount that remains unfilled before the bid is processed. The auction ends when there are no bids that can be filled left.
To simplify the process, all partially filled bids and asks could be determined as fully unsuccessful. Alternatively, partially filled bids and asks could be divided into two different bids or asks with filled part and unfilled part.

Every individual accepted bid will be a separate p2p loan contract with the parameters from the auction clearing results (lending amount, collateral, interest).
Every individual accepted ask will be a separate p2p loan contract with the parameters from the auction clearing results (borrowing amount, collateral, interest).
Successful bids and asks receive an NFT holding data on the contract between them and the auction smart contract. NFT’s can be transferred to third parties to transfer the rights or obligations of the NFT holder in relation to the auction contract, creating the possibility of aftermarkets.

This repository contains a demonstrative example on the auction clearing mechanism written in Python: auction.py 

# Loan payments after maturity expires
The counterparty of the individual bid and ask contracts is the auction contract. Auction contract will collect the paid loans and the interest from borrowers and distribute them to the lenders after deduction of the protocol fees. Distribution of paid loans and interests from the auction contract to the lenders is done based on the portion of the amount lent from the total lent amount and partition of interest of the total interest of all successful bids at the clearing of the auction. Borrower’s loans and interest is due to be paid in fixed time after the maturity expires.
 
# Liquidations
If the health factor of the loan goes below 1 the loan can be liquidated, and the proceedings will go to the liquidator and to the auction contract.

# User interface
Lenders and borrowers transact with the auction contract through an off-chain user interface. UI should display time until the auction closes, current valid bids and asks, data on how much of the bids or asks would be filled and what would the interest for the user be if the auction would be cleared with all current bids and asks. After the auction is closed, UI would display the final results of the auction, possible liquidations, and the time until the loans expire to be paid back to the auction contract by the lenders.
 
# Benefits of auction based lending
With auction based lending, cost of search for market participants is reduced compared to posted price offerings or negotiations between participants outside of a marketplace. 

Participants know with certainty the time of maturity and interest of the loan.

Lenders and borrowers can transact giving and taking loans for any amount of tokens not restricted to the amount of tokens on the opposing bids or asks, and with any of the maturities defined by the DAO to be available in different auction pools, and with an interest they accept.

Sequential market clearing (“Call market”) can be more efficient than a continuous market for bids and asks as it collects more supply and demand from a longer time to be cleared at once. This can be especially beneficial in a market with low liquidity and a small number of transactions.

More information on the efficiency of auction markets can be found for example in the following research paper about multi-attribute double auctions discussing similar markets to the auction market for lending and borrowing presented above:
 https://www.electronicmarkets.org/fileadmin/user_upload/doc/Issues/Volume_16/Issue_02/V16I2_Towards_Multi-Attribute_Double_Auctions_for_Financial_Markets.pdf

# Additional development opportunities with auction lending

Auto-renew lending bids and borrowing asks

Lenders making a bid can choose a parameter auto-renew to automatically move the liquidity of a successful bid to the following auctions. Interest for the next auction would be by default the same as for the bid that was successful in the previous auction, but it would be possible to change interest for the next auction during the maturity of the currently active loan until the next auction closing time (would need a separate parameter for the interest in the next auction). Unsuccessful bids are released from the auction pool regardless of auto-renew parameter value to prevent bids and asks with unserious interest to stay in the auction pool.
To make it possible for borrowers to renew their asks and lend automatically in the next auction the ask parameter of amount of tokens to be lent is needed. Then the borrower can make a bid with larger than minimum collateral and define the amount to be borrowed smaller than the maximum amount the collateral amount could give, and then the excess collateral assures that the collateral is large enough to auto-renew the loan in the next auction. Similarly to lending bids, the borrower could adjust the interest rate until the next auction closing time.
Borrowers auto-renew option should override the due time of payments of loan and interest of the previous auction until the next auction has cleared, so that the new loan can be used to pay the previous loan. If no bids are matching with the borrower's ask to renew the loan in the auction, then the borrower has three options: pay the loan and interest, increase interest in ask or let the loan get liquidated.

Possibility for borrower to add collateral to active loans

The borrower could add more collateral to the borrowing ask contract to prevent liquidation of an active loan or to make the ask in the next auction valid with enough collateral.
 
Volume based auction intervals

Auction bids and asks are matched in auctions periodically with intervals depending on the loan maturity and the supply and demand of loans. Interval of auctions could be automatically adjusted according to the market needs by making the auction ending time dependent on the volume of successful bids and asks with auction rules defining that the auction would have a soft ending time either at defined ending time or alternatively after volume exceeds some fixed threshold whichever occurs first. Next auction would be generated right after the previous auction has been cleared. For example, auctions for loans of 360 days maturity could be arranged every 30 days with 30 days duration of auction and have a soft ending time after the matched loans exceed 100000 ADA in value. Next auction would begin after the previous one would have been cleared. 

