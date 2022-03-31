from yoomoney import Client

TOKEN = '4100110291211346.F6BA470FC729FC83C5C9271492B7C3D3DB498154E011946C987DEE81D2E6B535AB9AA9DC14927179880DD1FC12D74E9EAF680AFFC083781B1D3327322DA26741B18F90BD25DEE45A925B308FA946CB0D50C6B8D02FA46FE5CC1E7907FB22B1C3F885F6C14C9502F93A3FF59BDEE4EE5338F43D24BA39B1617DE90B7525441099'
# from yoomoney import Quickpay
# quickpay = Quickpay(
#             receiver="4100110291211346",
#             quickpay_form="shop",
#             targets="Покупка VIP",
#             paymentType="SB",
#             sum=150,
#             )
client = Client(TOKEN)
history = client.operation_history(label="a1b2c3d4e5")
print("List of operations:")
print("Next page starts with: ", history.next_record)
print(history.operations)
for operation in history.operations:
    print()
    print("Operation:",operation.operation_id)
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