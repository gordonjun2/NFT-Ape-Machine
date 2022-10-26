import os
import time
import ast
from etherscan import Etherscan
from discord_webhook import DiscordWebhook, DiscordEmbed

## Input Etherscan API
eth = Etherscan("3JUNYUHPT9UKSZNM3UMX1WDB8P3TZXEHTH") # key in quotation marks

WEBHOOK_URL = ''

webhook = DiscordWebhook(url=WEBHOOK_URL, rate_limit_retry=True)

embed = DiscordEmbed(title="Running 'nft_ape_machine.py'", description='Scanning what NFT gods are buying / selling ...')
webhook.add_embed(embed)

response = webhook.execute()

## Read in NFT gods' wallet addresses (IT IS IMPORTANT THAT THE SEQUENCE OF THE WALLET IS NOT CHANGED. IF IT IS CHANGED, DELETE 'prev_check_ind_tokens.txt' and
## 'prev_check_tokens.txt'. However, you can add new NFT god addresses below.)
with open("nft_traders_addresses.txt") as file:
    lines = file.readlines()
    lines = [line.rstrip() for line in lines]
file.close()

## Create .txt that contains each NFT god transactions in the previous check separately

new_buy_file_flag = 0
new_sell_file_flag = 0

if os.path.exists('prev_check_ind_buy_tokens.txt')==False:  
    create_file= open("prev_check_ind_buy_tokens.txt",'w')  #This is just to  create the file in case it doesn't exist
    create_file.close()
    new_buy_file_flag = 1

if os.path.exists('prev_check_ind_sell_tokens.txt')==False:  
    create_file= open("prev_check_ind_sell_tokens.txt",'w')  #This is just to  create the file in case it doesn't exist
    create_file.close()
    new_sell_file_flag = 1

## Create .txt that contains all NFT god transactions in the previous check together

if os.path.exists('prev_check_buy_tokens.txt')==False:  
    create_file= open("prev_check_buy_tokens.txt",'w+')  #This is just to  create the file in case it doesn't exist
    create_file.close()

if os.path.exists('prev_check_sell_tokens.txt')==False:  
    create_file= open("prev_check_sell_tokens.txt",'w+')  #This is just to  create the file in case it doesn't exist
    create_file.close()

## Initialize inputs to API

wallet_addresses = []
nft_gods = []

total_gods = len(lines)

for line in lines:
    wallet_addresses.append(line.split()[1].split("/")[1].lower())
    if len(line.split()[2:]) > 1:
        nft_gods.append([" ".join(line.split()[2:])][0])
    else:
        nft_gods.append(line.split()[2:][0])

## API call

head_no = 20

print("===== NFT Gods and their purchases =====\n")

 # rerun_state = 0 means that the API calls will be done continuously in the 'while' loop, while rerun_state = 1 means that the API calls will be done once. 
 # Initially, rerun_state = 0 in order to get into the 'while' loop below. Immediately as it enters, rerun_state = 1 to prevent the continuous looping. Under
 # optimal state, the program will successfully execute all API calls under 'try'. However, it is possible that an API call is unsuccessful (Etherscan's issue).
 # This will cause an error that stops the program. To overcome this, the program will enter 'except' when this issue occurs and set rerun_state = 0 again. The
 # 'break' will cause the program to exit the 'for' loop. With rerun_state == 0, the 'while' loop restart. The program will only exit the 'while' loop if the 
 # data collection is fully successful. 

rerun_state = 0
rerun_num = 0      

def peek_line(f):
    pos = f.tell()
    line = f.readline()
    f.seek(pos)
    return line

while (rerun_state == 0):
    all_buy_tokens = set()
    all_new_buy_tokens = set()
    prev_check_ind_buy_tokens_line = []
    all_sell_tokens = set()
    all_new_sell_tokens = set()
    prev_check_ind_sell_tokens_line = []
    buy_file_var = open("prev_check_ind_buy_tokens.txt", "r+")
    sell_file_var = open("prev_check_ind_sell_tokens.txt", "r+")
    rerun_state = 1
    count = 0
    for wallet_address, god in zip(wallet_addresses, nft_gods):
        count = count + 1
        try:
            erc721_track_dict = eth.get_erc721_token_transfer_events_by_address(address=wallet_address, startblock = 0, endblock = 999999999, sort = 'desc')
        except:
            rerun_state = 0
            rerun_num = rerun_num + 1
            if (rerun_num == 10):
                rerun_state = 1
            else:
                print("Oops, there is an issue in retrieveing the data from Etherscan. Trying again ...")                           # TO DISPLAY IN TELEGRAM BOT

                webhook = DiscordWebhook(url=WEBHOOK_URL, rate_limit_retry=True)
                embed = DiscordEmbed(title="Oops, there is an issue in retrieveing the data from Etherscan. Trying again ...")
                webhook.add_embed(embed)

                response = webhook.execute()
            break
        erc721_track_dict_head = erc721_track_dict[:head_no]
        buy_tokens_head = [dict["tokenName"] for dict in erc721_track_dict_head if dict["to"] == wallet_address]
        buy_unique_head = [i for n, i in enumerate(buy_tokens_head) if i not in buy_tokens_head[:n]]
        sell_tokens_head = [dict["tokenName"] for dict in erc721_track_dict_head if dict["from"] == wallet_address]
        sell_unique_head = [i for n, i in enumerate(sell_tokens_head) if i not in sell_tokens_head[:n]]
        if (new_buy_file_flag == 0 and peek_line(buy_file_var) != ''):
            prev_buy_unique_head = ast.literal_eval(buy_file_var.readline())
            new_buy_tokens = set(buy_unique_head) - set(prev_buy_unique_head)
            if (len(new_buy_tokens) > 0):
                buy_description = "Bought " + str(new_buy_tokens)
                print(str(god) + " bought " + str(new_buy_tokens) + " token(s) since the previous check.")       # TO DISPLAY IN TELEGRAM BOT
                all_new_buy_tokens.update(new_buy_tokens)
            else:
                buy_description = "Bought nothing"
                print(str(god) + " did not buy any token(s) since the previous check.")                          # TO DISPLAY IN TELEGRAM BOT
        else:
            if (len(new_buy_tokens) > 0):
                buy_description = "Bought " + str(buy_unique_head)
                print(str(god) + " bought " + str(buy_unique_head) + " token(s) since the previous check.")      # TO DISPLAY IN TELEGRAM BOT
                all_new_buy_tokens.update(buy_unique_head)
            else:
                buy_description = "Bought nothing"
                print(str(god) + " did not buy any token(s) since the previous check.")                          # TO DISPLAY IN TELEGRAM BOT

        if (new_sell_file_flag == 0 and peek_line(sell_file_var) != ''):
            prev_sell_unique_head = ast.literal_eval(sell_file_var.readline())
            new_sell_tokens = set(sell_unique_head) - set(prev_sell_unique_head)
            if (len(new_sell_tokens) > 0):
                sell_description = "Sold " + str(new_sell_tokens)
                print(str(god) + " sold " + str(new_sell_tokens) + " token(s) since the previous check.")                          # TO DISPLAY IN TELEGRAM BOT
                print("\n")
                all_new_sell_tokens.update(new_sell_tokens)
            else:
                sell_description = "Sold nothing"
                print(str(god) + " did not sell any token(s) since the previous check.")                          # TO DISPLAY IN TELEGRAM BOT
                print("\n")
        else:
            if (len(new_sell_tokens) > 0):
                sell_description = "Sold " + str(sell_unique_head)
                print(str(god) + " sold " + str(sell_unique_head) + " token(s) since the previous check.")                             # TO DISPLAY IN TELEGRAM BOT
                print("\n")
                all_new_sell_tokens.update(sell_unique_head)
            else:
                sell_description = "Sold nothing"
                print(str(god) + " did not sell any token(s) since the previous check.")                          # TO DISPLAY IN TELEGRAM BOT
                print("\n")

        description_text = buy_description + '\n' + sell_description

        webhook = DiscordWebhook(url=WEBHOOK_URL, rate_limit_retry=True)

        embed = DiscordEmbed(title="(" + str(count) + "/" + str(total_gods) + ") " + str(god) + "'s latest transactions: ", description=description_text)
        webhook.add_embed(embed)

        response = webhook.execute()

        prev_check_ind_buy_tokens_line.append(buy_unique_head)
        all_buy_tokens.update(buy_unique_head)
        prev_check_ind_sell_tokens_line.append(sell_unique_head)
        all_sell_tokens.update(sell_unique_head)
        time.sleep(0.5)
    buy_file_var.close()
    sell_file_var.close()

if (rerun_num == 5):
    print('Unable to retrieve data from Etherscan. Try again later.')                                                             # TO DISPLAY IN TELEGRAM BOT

    webhook = DiscordWebhook(url=WEBHOOK_URL, rate_limit_retry=True)

    embed = DiscordEmbed(title="Unable to retrieve data from Etherscan. Try again later.")
    webhook.add_embed(embed)

    response = webhook.execute()

else:
    # print("Buy Summary: " + str(list(all_buy_tokens)))
    # print("\nSell Summary: " + str(list(all_sell_tokens)))

    if (len(all_new_buy_tokens) > 0):
        print("Summary of new tokens bought since the previous check: " + str(list(all_new_buy_tokens)))                          # TO DISPLAY IN TELEGRAM BOT
    else:
        print("No new tokens bought since the previous check.")                                                               # TO DISPLAY IN TELEGRAM BOT

    if (len(all_new_sell_tokens) > 0):
        print("\nSummary of new tokens sold since the previous check: " + str(list(all_new_sell_tokens)))                          # TO DISPLAY IN TELEGRAM BOT
    else:
        print("\nNo new tokens sold since the previous check.")                                                               # TO DISPLAY IN TELEGRAM BOT

    ## Save data into .txt to be used for the next check

    file_var = open('prev_check_ind_buy_tokens.txt', 'w+')
    file_var.writelines("%s\n" % i for i in prev_check_ind_buy_tokens_line)
    file_var.close()

    file_var = open('prev_check_ind_sell_tokens.txt', 'w+')
    file_var.writelines("%s\n" % i for i in prev_check_ind_sell_tokens_line)
    file_var.close()

    file_var = open('prev_check_buy_tokens.txt', "w+")
    file_var.write(str(all_buy_tokens))
    file_var.close()

    file_var = open('prev_check_sell_tokens.txt', "w+")
    file_var.write(str(all_sell_tokens))
    file_var.close()

    print("\n===== Stay tune for next update! =====")

    webhook = DiscordWebhook(url=WEBHOOK_URL, rate_limit_retry=True)

    embed = DiscordEmbed(title="Stay tune for next update!")
    webhook.add_embed(embed)

    response = webhook.execute()


