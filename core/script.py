from globalConfig import groupIDs,botID,adminIDs
from model import User,Stock,Debt
from user import *
from static import *
from extract import *
from market import *
from stock import *
from debt import *
from industrial import *

commands:dict={}

def register(funcStr: str,func: callable):
    """
    向bot注册命令
    :param funcStr: 功能
    :param func: 功能函数
    """
    commands[funcStr]=func


def registerByDict(registers: dict[str,callable]):
    for funcStr,func in registers.items():
        register(funcStr,func)

def dealWithRequest(funcStr:str,messageList:list[str],qid:str):
    if funcStr in commands:
        ans=commands[funcStr](messageList,qid)
    else:
        ans="未知命令:请输入'帮助'以获取帮助信息！"
    return ans

def handle(res,group):
    ans:str=''  #回复给用户的内容
    if group:#是群发消息
        message:str=res.get("raw_message")
        qid:str=str(res.get('sender').get('user_id'))  #发消息者的qq号
        gid:str=str(res.get('group_id'))  #群的qq号
        if gid not in groupIDs:
            return None
        if "[CQ:at,qq=%s]"%botID not in message:#必须在自己被at的情况下才能作出回复
            return None

        messageList:list=message.split(' ')
        funcStr:str=messageList[1]
        messageList.pop(0)  #忽略at本身

        try:
            ans='[CQ:at,qq=%s]'%qid+dealWithRequest(funcStr,messageList,qid)
            send(gid,ans,group=True)
        except AssertionError as err:
            send(gid,err,group=True)

    else:
        message:str=res.get("raw_message")
        qid:str=str(res.get('sender').get('user_id'))
        messageList:list=message.split(' ')
        funcStr:str=messageList[0]

        try:
            ans=dealWithRequest(funcStr,messageList,qid)
            send(qid,ans,group=False)
        except AssertionError as err:
            send(qid,err,group=False)

def distraint(messageList:list[str],qid:str):
    """
    强制执行
    :param messageList: 强制执行 被执行人学号/qid 被执行的命令名 *被执行的命令参数
    :param qid:
    :return: 提示信息
    """
    assert len(messageList) >= 3, '强制执行失败：输入格式不正确！'
    assert qid in adminIDs, '您无权进行强制执行！'
    identifier = messageList[1]
    if identifier.startswith("q"):
        # 通过QQ号查找对方
        tqid: str = identifier[1:]
        target: User = User.find(tqid, mysql)
        assert target, "强制执行失败:QQ号为%s的用户未注册！" % tqid
    else:
        tschoolID: str = identifier
        # 通过学号查找
        assert User.findAll(mysql, 'schoolID=?', (tschoolID,)), "强制执行失败:学号为%s的用户未注册！" % tschoolID
        target: User = User.findAll(mysql, 'schoolID=?', (tschoolID,))[0]
        tqid = target.qid

    funcStr = messageList[2]

    return commands[funcStr](messageList[2:],tqid)

def treasuryAction(messageList:list[str],qid:str):
    """
    国库财政行动
    :param messageList: 国库 被执行的命令名 *被执行的命令参数
    :param qid:
    :return: 提示信息
    """
    assert len(messageList) >= 2, '国库行动失败：输入格式不正确！'
    assert qid in adminIDs, '您无权调用国库经费！'

    funcStr = messageList[1]

    return commands[funcStr](messageList[1:],'treasury')

       
registerByDict({
    "time":returnTime,
    "帮助":getHelp,
    "注册":signup,
    "查询":getUserInfo,
    "开采":getMineral,
    "开放":openMine,
    "兑换":exchangeMineral,
    "预售":presellMineral,
    "购买":buyMineral,
    "预订":prebuyMineral,
    "售卖":sellMineral,
    "拍卖":preauctionMineral,
    "投标":bidMineral,
    "矿市":mineralMarket,
    "发行":issueStock,
    "认购":acquireStock,
    "买入":buyStock,
    "抛出":sellStock,
    "股市":stockMarket,
    "支付":pay,
    "放贷":prelendDebt,
    "借贷":borrowDebt,
    "还款":repayDebt,
    "转让债务":transferDebt,
    "免除":forgiveDebt,
    "债市":debtMarket,
    "分解":decompose,
    "合成":synthesize,
    "修饰":decorate,
    "复制":duplicate,
    "炼化":refine,
    "建设":build,
    "科研":research,
    "勘探":discover,
    "取消":cancelPlan,
    "执行":enactPlan,
    "计划":showPlan,
    "转让工厂":transferFactory,
    "转让矿井":transferMine,
    "强制执行":distraint,
    "国库":treasuryAction,
    "抽奖":lottery,
    "因子查询":factorsLookup,
})

def assetCalculation(user:User):
    assets = user.money
    for i in user.stocks.items():
        stock = Stock.find(i[0], mysql)
        assets += i[1] * stock.price
    for debt in Debt.findAll(mysql, 'creditor=?', (user.qid,)):
        assets += debt.money

    return assets
