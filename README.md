# LabgeniusSystem
New labgenius system for Raspberry pi

# Labgenius api test(emulator)
모든 결과 값은 json 으로 반환 됩니다.

1. PCR Start
	- http://{hostname}.local:6009/api/task/start
	- PCR 이 이미 시작되었으면, 에러를 반환합니다.

2. PCR Stop
	- http://{hostname}.local:6009/api/task/stop
	- PCR 이 실행중이지 않은 경우, 에러를 반환합니다.

3. PCR Status
	- http://{hostname}.local:6009/api/task/status
	- GUI 에 보여주기 위한 모든 PCR 정보를 반환합니다.
	- 현재 에러정보는 포함되지 않습니다.

	- (2019-08-13 Added) 프로토콜 이름과 필터 정보가 추가되었습니다.


# Protocol functions

1. Protocol list
	- http://{hostname}.local:6009/api/protocol/list
	- 모든 프로토콜 리스트를 확인할 수 있습니다.
	- 프로토콜마다 필드는 아래와 같이 있습니다.
	- idx, protocolName, filters, created_date, protocol data
	- 해당 필드들은 다른 프로토콜에서도 사용되므로(특히 idx 값) 반드시 로컬 변수에 저장하여 사용하세요.
	- 테스트를 위한 GET Method 도 지원하며, 공식적으로는 POST 방식만 사용하세요.

2. Protocol select
	- http://{hostname}.local:6009/api/protocol/select
	- 사용할 프로토콜을 선택할 수 있습니다.
	- POST 방식만 사용가능하며, 데이터로 idx 를 받습니다(text 타입으로 숫자 값만 보내주세요).
	- idx 값을 위의 list API 에서 얻을 수 있으며, 이외의 값은 에러를 반환합니다.
	- select 시 최근 프로토콜에 저장되며, 이 값은 저장된 프로토콜 목록에서 제거하거나 수정해도 변경되지 않습니다.

3. Check protocol data
	- http://{hostname}.local:6009/api/protocol/check
	- 프로토콜 데이터의 유효성을 판단합니다.
	- POST 방식만 사용가능하며, filter 값을 포함한 전체 프로토콜 리스트를 받습니다.
	- text 타입으로 값을 전달해주세요.
	- 각 프로토콜 라인은 "\r\n" 로 구분됩니다.
	- 맨 첫줄에는 프로토콜 필터 값이 ", " 로 구분되어 있어야 합니다.
	- 필터의 종류는 FAM, HEX, ROX, CY5 이며 대문자로만 받습니다.
	- 입력 오류에 틀린 라인과 함께 어떤 점이 틀렸는지 이유가 반환됩니다.
	- 필요에 의하여 추후에 한글로 반환되도록 수정 가능합니다.

4. Create protocol
	- http://{hostname}.local:6009/api/protocol/new
	- 프로토콜 생성에서 사용되는 API 입니다.
	- 내부적으로 check api 루틴을 돌게 되지만, 사용시에는 check API 후에 new API 를 호출해주세요.
	- 데이터는 check API 와 동일하게 받지만, 맨 윗줄에 프로토콜 이름이 추가되어 보내야 합니다.
	- 각 프로토콜 라인은 "\r\n" 로 구분됩니다.
	- 첫 줄은 프로토콜 이름, 두번째 줄은 필터, 세번째 줄부터 프로토콜 데이터 입니다.
	- 필터의 종류는 FAM, HEX, ROX, CY5 이며 대문자로만 받습니다.
	- 입력 오류에 틀린 라인과 함께 어떤 점이 틀렸는지 이유가 반환됩니다.
	- text 타입으로 값을 전달해주세요.

5. Edit protocol
	- http://{hostname}.local:6009/api/protocol/edit
	- 프로토콜을 수정하기 위한 기능입니다.
	- POST 방식으로만 사용가능하며, 맨 윗줄에 idx 값과 변경할 프로토콜 데이터를 받습니다.
	- 각 프로토콜 라인은 "\r\n" 로 구분됩니다.
	- 첫 줄은 idx 값, 두번째 줄은 필터, 세번째 줄부터 프로토콜 데이터 입니다.
	- 필터의 종류는 FAM, HEX, ROX, CY5 이며 대문자로만 받습니다.
	- 입력 오류에 틀린 라인과 함께 어떤 점이 틀렸는지 이유가 반환됩니다.
	- text 타입으로 값을 전달해주세요.

6. Delete protocol
	- http://{hostname}.local:6009/api/protocol/delete
	- 프로토콜을 삭제하기 위한 기능입니다.
	- POST 방식으로만 사용가능하며, 맨 윗줄에 idx 값을 받습니다.
	- idx 값을 위의 list API 에서 얻을 수 있으며, 이외의 값은 에러를 반환합니다.
	- text 타입으로 값을 전달해주세요.

# History functions

1. List History
	- http://{hostname}.local:6009/api/history/list
	- 모든 PCR 결과 리스트를 확인할 수 있습니다.

2. Graph data History
	- http://{hostname}.local:6009/api/history/graphdata
	- 특정 PCR 결과의 형광 밝기값을 얻기 위한 API 입니다.

3. Temperature data history
	- http://{hostname}.local:6009/api/history/tempdata
	- 특정 PCR 결과의 온도 값을 얻기 위한 API 입니다.
	
# TODO list

1. Chip 관련 프로토콜 구성
2. Chip protocol 에 대한 구성
3. Chip 데이터 저장을 위한 database 구성.
4. Chip Emulator 구현

5. PCR Emulator 대신 실제 장비 테스트
6. ZMQ 기능 테스트 및 타임 아웃 기능 추가.