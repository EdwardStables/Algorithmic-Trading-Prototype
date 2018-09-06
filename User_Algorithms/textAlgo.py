import platformHelper as pH


test1 = pH.getData("test 1")
test = pH.getData("test")
pH.setData("new test 1", test1)
pH.setData("does it fucking work yet", test)
print(pH.getDataList())