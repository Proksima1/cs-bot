from yoomoney import Client

TOKEN = '4100117742745846.6C709A1EE00C194B504067D9ECDDAD54A459BA3074D13008665B624116D5D838F40F93A4D75F8C099231D2551B060E74401F3FE3FE262C43A9BD6FBCBA0195DB2DD8FFDE259680FF1037DBF45B970C18E9F7CD0E801EEC798C84EC4AAD86E1AB07EB78708043C93CA5755C55FADCE4EBA77387C9DD0881C63AE894368B200593'
"""A4F7B77D0602DDCAC557350ED720F3DCDC7C70D5C64111E159D88DC6A8C7AC72"""
# from yoomoney import Authorize
#
# Authorize(
#       client_id="A4F7B77D0602DDCAC557350ED720F3DCDC7C70D5C64111E159D88DC6A8C7AC72",
#       redirect_uri="https://t.me/VIP_WarSkins_bot",
#       scope=["account-info",
#              "operation-history",
#              "operation-details",
#              "incoming-transfers",
#              "payment-p2p",
#              "payment-shop",
#              ]
#       )
# from yoomoney import Quickpay
# quickpay = Quickpay(
#             receiver="4100110291211346",
#             quickpay_form="shop",
#             targets="Покупка VIP",
#             paymentType="SB",
#             sum=150,
#             )
client = Client(TOKEN)
history = client.operation_history(label="E94gqCQavp")
# print(history.operations)
print("List of operations:")
print("Next page starts with: ", history.next_record)
print(history.operations)
for operation in history.operations:
    print()
    print("Operation:", operation.operation_id)
    print("\tStatus     -->", operation.status)
    print("\tDatetime   -->", operation.datetime)
    print("\tTitle      -->", operation.title)
    print("\tPattern id -->", operation.pattern_id)
    print("\tDirection  -->", operation.direction)
    print("\tAmount     -->", operation.amount)
    print("\tLabel      -->", operation.label)
    print("\tType       -->", operation.type)
# print(quickpay.base_url)
# print(quickpay.redirected_url)