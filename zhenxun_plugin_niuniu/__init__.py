from nonebot import on_command
from nonebot.params import CommandArg, Arg, ArgStr
from .until import init_rank
from utils.utils import is_number
from utils.message_builder import image , at
from utils.image_utils import text2image
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
  Bot,
  GroupMessageEvent,
  MessageEvent,
  MessageSegment,
  Message)
from .data_source import random_long
from PIL import Image
from io import BytesIO
from decimal import Decimal as de
import os
import ujson
import time
import base64
import random

__zx_plugin_name__ = "牛牛大作战"
__plugin_usage__ = """
usage：
    牛子大作战(误

    注册牛子 --注册你的牛子
    jj [@user] --与注册牛子的人进行击剑，对战结果影响牛子长度
    我的牛子 --查看自己牛子长度
    牛子长度排行 --查看本群正数牛子长度排行
    牛子深度排行 --查看本群负数牛子深度排行
    打胶 --对自己的牛子进行操作，结果随机
""".strip()
__plugin_des__ = "牛子大作战(误"
__plugin_type__ = ("群内小游戏",)
__plugin_cmd__ = ["注册牛子", "击剑/jj/JJ/Jj/jJ", "我的牛子", "牛子长度排行","牛子深度排行", "打胶", "牛牛大作战"]
__plugin_version__ = 0.3
__plugin_author__ = "molanp"
__plugin_settings__ = {
    "level": 5,
    "default_status": True,
    "limit_superuser": False,
    "cmd": ['注册牛子','击剑', 'jj', 'JJ', 'Jj', 'jJ', '我的牛子', '牛子长度排行','牛子深度排行', '打胶', '牛牛大作战'],
}

niuzi_register = on_command("注册牛子", priority=5, block=True)
niuzi_fencing = on_command("击剑", aliases={'JJ', 'Jj', 'jJ','jj'}, priority=5, block=True)
niuzi_my = on_command("我的牛子", priority=5, block=True)
niuzi_ranking = on_command("牛子长度排行", priority=5, block=True)
niuzi_ranking_e = on_command("牛子深度排行", priority=5, block=True)
niuzi_hit_glue = on_command("打胶", priority=5, block=True)
niuzi_zhuxiao = on_command("注销牛子",priority=5,block=True)
niuzi_he = on_command("他的牛子", aliases={'她的牛子','ta的牛子'},priority=5, block=True)


group_user_jj = {}
group_hit_glue = {}

path = os.path.dirname(__file__)

def readInfo(file, info=None):
    with open(os.path.join(path, file), "r", encoding="utf-8") as f:
        context = f.read()
        if info != None:
            with open(os.path.join(path, file), "w", encoding="utf-8") as f:
                f.write(ujson.dumps(info, indent=4, ensure_ascii=False))
            with open(os.path.join(path, file), "r", encoding="utf-8") as f:
                data = f.read()
            return {"data": ujson.loads(context.strip())}
        else:
            return ujson.loads(context.strip())

def get_all_users(group):
    group = readInfo("data/long.json")[group]
    return group

@niuzi_zhuxiao.handle()
async def _(event: GroupMessageEvent, state: T_State):
  group = str(event.group_id)
  qq = str(event.user_id)
  content = readInfo("data/long.json")
  niuzi_long = de(str(content[group][qq]))
  if niuzi_long > 0:
    niuzi_long = niuzi_long - 10
    result = "牛子注销失败！牛子减少10cm"
    content[group][qq] = niuzi_long
    readInfo('data/long.json',content)
  else:
    result = "你的牛子还没不够长，无法注销哦"
  await niuzi_zhuxiao.finish(Message(result),at_sender=True)

@niuzi_he.handle()
async def _(event: GroupMessageEvent, state: T_State):
  qq = str(event.user_id)
  group = str(event.group_id)
  content = readInfo("data/long.json")
  msg = event.get_message()
  at_list = []
  for msg_seg in msg:
    if msg_seg.type == "at":
      at_list.append(msg_seg.data["qq"])
      at = str(at_list[0])
  try:
    he_long = content[group][at]
    if he_long <= -50:
      result = f"嗯....好像已经穿过了身体吧..从另一面来看也可以算是凸出来的吧?当前深度{he_long}cm"
    elif -50 < he_long <= -25:
      result = random.choice([
        f"这名女生的身体很健康哦！当前深度{he_long}cm",
        f"WOW,真的凹进去了好多呢！当前深度{he_long}cm",
        f"ta已经是我们女孩子的一员啦！当前深度{he_long}cm"
      ])
    elif -25 < he_long <= -10:
      result = random.choice([
        f"ta已经是一名女生了呢，当前深度{he_long}cm",
        f"从女生的角度来说，你发育良好(,当前深度{he_long}cm",
        f"你醒啦？ta已经是一名女孩子啦！深度足足有{he_long}cm呢！",
        f"唔....可以放进去一根手指了都....当前深度{he_long}cm"
      ])
    elif -10 < he_long <= 0:
      result = random.choice([
        f"安了安了，不要伤心嘛，做女生有什么不好的啊。当前深度{he_long}cm",
        f"不哭不哭，摸摸头，虽然很难再长出来，但是请不要伤心啦啊！当前深度{he_long}cm",
        f"加油加油！我看好你哦！当前ta的深度{he_long}cm",
        f"你醒啦？ta现在已经是一名女孩子啦！当前深度{he_long}cm"
      ])
    elif 0 < he_long <= 10:
      result = random.choice([
        f"行不行啊？细狗！牛子长度才{he_long}cm！",
        f"虽然短，但是...emmm....但是虽然短。当前长度{he_long}cm",
        f"当前牛子长度{he_long}cm！！！"
      ])
    elif 10 < he_long <= 25:
      result = random.choice([
        f"唔，当前牛子长度是{he_long}cm",
        f"已经很长呢！当前长度{he_long}cm"
      ])
    elif 25 < he_long <= 50:
      result = random.choice([
        f"话说这种真的有可能吗？当前牛子长度{he_long}cm",
        f"牛子长度居然是{he_long}cm呢！！！"
      ])
    elif 50 < he_long:
      result = random.choice([
        f"已经突破天际了嘛...当前牛子长度{he_long}cm",
        f"唔...这玩意应该不会变得比我高吧？当前牛子长度{he_long}cm"
      ])
  except KeyError:
    result = "ta还没有牛子呢！"
  finally:
    await niuzi_he.finish(Message(result),at_sender=True)



@niuzi_register.handle()
async def _(event: GroupMessageEvent, state: T_State):
  group = str(event.group_id)
  qq = str(event.user_id)
  content = readInfo("data/long.json")
  long = random_long()    
  try:
    if content[group]:
      pass
  except KeyError:
    content[group] = {}
  try:
    if content[group][qq]:
      await niuzi_register.finish(Message("你已经注册过牛子啦！"), at_sender=True)
  except KeyError:
    content[group][qq] = long
    readInfo('data/long.json', content)
    await niuzi_register.finish(Message(f"注册牛子成功，当前长度{long}cm"), at_sender=True)

@niuzi_fencing.handle()
async def _(event: GroupMessageEvent, state: T_State):
  qq = str(event.user_id)
  group = str(event.group_id)
  global group_user_jj
  try:
    if group_user_jj[group]:
      pass
  except KeyError:
    group_user_jj[group] = {}
  try:
    if group_user_jj[group][qq]:
      pass
  except KeyError:
    group_user_jj[group][qq] = {}
  try:
    time_pass = int(time.time() - group_user_jj[group][qq]['time'])
    if time_pass < 180:
      time_rest = 180 - time_pass
      jj_refuse = [
        f'才过去了{time_pass}s时间,你就又要击剑了，真是饥渴难耐啊',
        f'不行不行，你的身体会受不了的，歇{time_rest}s再来吧',
        ]
      await niuzi_fencing.finish(random.choice(jj_refuse), at_sender=True)
  except KeyError:
    pass
  #
  msg = event.get_message()
  content = readInfo("data/long.json")
  at_list = []
  for msg_seg in msg:
    if msg_seg.type == "at":
      at_list.append(msg_seg.data["qq"])
  try:
    my_long = de(str(content[group][qq]))
    if len(at_list) >= 1:
      at = str(at_list[0])
      if len(at_list) >= 2:
        result = "一战多？你的小身板扛得住吗？"
      elif at != qq:
        try:
          opponent_long = de(str(content[group][at]))
          group_user_jj[group][qq]['time'] = time.time()
          if opponent_long > my_long:
            probability = random.randint(1, 100)
            if 0 < probability <= 69:
              reduce = random_long()
              my_long = my_long - reduce
              if my_long < 0:
                result = random.choice([
                  f"哦吼！？看来你的牛子因为击剑而凹进去了呢！凹进去了{format(reduce,'.2f')}cm！",
                  f"由于对方击剑技术过于高超，造成你的牛子凹了进去呢！凹进去了深{format(reduce,'.2f')}cm哦！",
                  f"好惨啊，本来就不长的牛子现在凹进去了呢！凹进去了{format(reduce,'.2f')}cm呢！"
                ])
              else:
                result = f"对方以绝对的长度让你屈服了呢！你的长度减少{format(reduce,'.2f')}cm，当前长度{format(my_long,'.2f')}cm！对方增加相应的长度"
              opponent_long = opponent_long + reduce
              content[group][qq] = my_long
              content[group][at] = opponent_long
              readInfo('data/long.json',content)
              
            else:
              reduce = random_long()
              opponent_long = opponent_long - reduce
              my_long = my_long + reduce
              if my_long < 0:
                result = random.choice([
                  f"哦吼！？你的牛子在长大欸！长大了{format(reduce,'.2f')}cm！",
                  f"牛子凹进去的深度变浅了欸！变浅了{format(reduce,'.2f')}cm！"
                ])
              else:
                result = f"虽然你不够长，但是你逆袭了呢！你的长度增加{format(reduce,'.2f')}cm，当前长度{format(my_long,'.2f')}cm！对方减少相应的长度"
              content[group][qq] = my_long
              content[group][at] = opponent_long
              readInfo('data/long.json',content)
              
          elif my_long > opponent_long:
            probability = random.randint(1, 100)
            if 0 < probability <= 80:
              reduce = random_long()
              opponent_long = opponent_long - reduce
              my_long = my_long + reduce
              if my_long < 0:
                result = random.choice([
                  f"哦吼！？你的牛子在长大欸！长大了{format(reduce,'.2f')}cm！",
                  f"牛子凹进去的深度变浅了欸！变浅了{format(reduce,'.2f')}cm！"
                ])
              else:
                result = f"你以绝对的长度让对方屈服了呢！你的长度增加{format(reduce,'.2f')}cm，当前长度{format(my_long,'.2f')}cm！对方减少相应的长度"
              content[group][qq] = my_long
              content[group][at] = opponent_long
              readInfo('data/long.json',content)
            else:
              reduce = random_long()
              my_long = my_long - reduce
              if my_long < 0:
                result = random.choice([
                  f"哦吼！？看来你的牛子因为击剑而凹进去了呢！目前深度{format(reduce,'.2f')}cm！",
                  f"由于对方击剑技术过于高超，造成你的牛子凹了进去呢！当前深度{format(reduce,'.2f')}cm！",
                  f"好惨啊，本来就不长的牛子现在凹进去了呢！凹进去了{format(reduce,'.2f')}cm！"
                ])
              else:
                result = f"虽然你比较长，但是对方逆袭了呢！你的长度减少{format(reduce,'.2f')}cm，当前长度{format(my_long,'.2f')}cm！对方增加相应的长度"
              opponent_long = opponent_long + reduce
              content[group][qq] = my_long
              content[group][at] = opponent_long
              readInfo('data/long.json',content)
        except KeyError:
          result = "对方还没有牛子呢，你不能和ta击剑！"
      else:
        result = "不能和自己击剑哦！"
    else:
      result = "你要和谁击剑？你自己吗？"
  except KeyError:
    del group_user_jj[group][qq]['time']
    result = "你还没有牛子呢！不能击剑！"
  finally:
    await niuzi_fencing.finish(Message(result),at_sender=True)

@niuzi_my.handle()
async def _(event: GroupMessageEvent, state: T_State):
  qq = str(event.user_id)
  group = str(event.group_id)
  content = readInfo("data/long.json")
  try:
    my_long = content[group][qq]
    if my_long <= -50:
      result = f"嗯....好像已经穿过了身体吧..从另一面来看也可以算是凸出来的吧?当前深度{format(my_long,'.2f')}cm"
    elif -50 < my_long <= -25:
      result = random.choice([
        f"这名女生，你的身体很健康哦！当前深度{format(my_long,'.2f')}cm",
        f"WOW,真的凹进去了好多呢！当前深度{format(my_long,'.2f')}cm",
        f"你已经是我们女孩子的一员啦！当前深度{format(my_long,'.2f')}cm"
      ])
    elif -25 < my_long <= -10:
      result = random.choice([
        f"你已经是一名女生了呢，当前深度{format(my_long,'.2f')}cm",
        f"从女生的角度来说，你发育良好(,当前深度{format(my_long,'.2f')}cm",
        f"你醒啦？你已经是一名女孩子啦！深度足足有{format(my_long,'.2f')}cm呢！",
        f"唔....可以放进去一根手指了都....当前深度{format(my_long,'.2f')}cm"
      ])
    elif -10 < my_long <= 0:
      result = random.choice([
        f"安了安了，不要伤心嘛，做女生有什么不好的啊。当前深度{format(my_long,'.2f')}cm",
        f"不哭不哭，摸摸头，虽然很难再长出来，但是请不要伤心啦啊！当前深度{format(my_long,'.2f')}cm",
        f"加油加油！我看好你哦！当前深度{format(my_long,'.2f')}cm",
        f"你醒啦？你现在已经是一名女孩子啦！当前深度{format(my_long,'.2f')}cm"
      ])
    elif 0 < my_long <= 10:
      result = random.choice([
        f"你行不行啊？细狗！牛子长度才{format(my_long,'.2f')}cm！",
        f"虽然短，但是...emmm....但是虽然短。当前长度{format(my_long,'.2f')}cm",
        f"当前牛子长度{format(my_long,'.2f')}cm！！！"
      ])
    elif 10 < my_long <= 25:
      result = random.choice([
        f"唔，当前牛子长度是{format(my_long,'.2f')}cm",
        f"已经很长呢！当前长度{format(my_long,'.2f')}cm"
      ])
    elif 25 < my_long <= 50:
      result = random.choice([
        f"话说这种真的有可能吗？当前牛子长度{format(my_long,'.2f')}cm",
        f"牛子长度居然是{format(my_long,'.2f')}cm呢！！！"
      ])
    elif 50 < my_long:
      result = random.choice([
        f"已经突破天际了嘛...当前牛子长度{format(my_long,'.2f')}cm",
        f"唔...这玩意应该不会变得比我高吧？当前牛子长度{format(my_long,'.2f')}cm"
      ])
  except KeyError:
    result = "你还没有牛子呢！"
  finally:
    await niuzi_my.finish(Message(result),at_sender=True)

@niuzi_ranking.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    num = arg.extract_plain_text().strip()
    if is_number(num) and 51 > int(num) > 10:
        num = int(num)
    else:
        num = 10
    all_users = get_all_users(str(event.group_id))
    all_user_id = []
    all_user_data = []
    for user_id, user_data in all_users.items():
      if user_data > 0:
        all_user_id.append(int(user_id))
        all_user_data.append(user_data)
    
    if len(all_user_id)!=0: 
      rank_image = await init_rank("牛子长度排行榜-单位cm", all_user_id, all_user_data, event.group_id, num)
      if rank_image:
          await niuzi_ranking.finish(image(b64=rank_image.pic2bs4()))
    else: 
      await niuzi_ranking.finish(Message("暂无此排行榜数据...", at_sender=True))
        
@niuzi_ranking_e.handle()
async def _(event: GroupMessageEvent, arg: Message = CommandArg()):
    num = arg.extract_plain_text().strip()
    if is_number(num) and 51 > int(num) > 10:
        num = int(num)
    else:
        num = 10
    all_users = get_all_users(str(event.group_id))
    all_user_id = []
    all_user_data = []
    for user_id, user_data in all_users.items():
      if user_data < 0:
        all_user_id.append(int(user_id))
        all_user_data.append(float(str(user_data)[1:]))
    
    if len(all_user_id)!= 0: 
      rank_image = await init_rank("牛子深度排行榜-单位cm", all_user_id, all_user_data, event.group_id, num)
      if rank_image:
          await niuzi_ranking_e.finish(image(b64=rank_image.pic2bs4()))
    else: 
      await niuzi_ranking_e.finish(Message("暂无此排行榜数据..."), at_sender=True)


@niuzi_hit_glue.handle()
async def _(event: GroupMessageEvent, state: T_State):
  qq = str(event.user_id)
  group = str(event.group_id)
  global group_hit_glue
  try:
    if group_hit_glue[group]:
      pass
  except KeyError:
    group_hit_glue[group] = {}
  try:
    if group_hit_glue[group][qq]:
      pass
  except KeyError:
    group_hit_glue[group][qq] = {}
  try:
    time_pass = int(time.time() - group_hit_glue[group][qq]['time'])
    if time_pass < 180:
      time_rest = 180 - time_pass
      glue_refuse = [
        f'才过去了{time_pass}s时间,你就又要打胶了，身体受得住吗',
        f'不行不行，你的身体会受不了的，歇{time_rest}s再来吧'
        ]
      await niuzi_hit_glue.finish(random.choice(glue_refuse), at_sender=True)
  except KeyError:
    pass
  try:
    content = readInfo("data/long.json")
    my_long = de(str(content[group][qq]))
    group_hit_glue[group][qq]['time'] = time.time()
    probability = random.randint(1, 100)
    if 0 < probability <= 40:
      reduce = random_long()
      my_long = my_long + reduce
      result = random.choice([
        f"你的打胶促进了牛子发育，牛子增加{format(reduce,'.2f')}cm了呢！",
        f"你的牛子在众人震惊的目光下增加了{format(reduce,'.2f')}cm呢！"
        ])
    elif 40 < probability <= 60:
      result = random.choice([
        "你打了个胶，什么变化也没有",
        "你的牛子刚开始变长了，可过了一会又回来了，什么变化也没有"
        ])
    else:
      reduce = random_long()
      my_long = my_long - reduce
      if my_long < 0:
        result = random.choice([
          f"哦吼！？看来你的牛子凹进去了{format(reduce,'.2f')}cm呢！",
          f"你因为打胶过度导致牛子凹了进去{format(reduce,'.2f')}cm呢！"
        ])
      else:
        result = random.choice([
          f"阿哦，你过度打胶，牛子缩短{format(reduce,'.2f')}cm了呢！",
          f"你的牛子变长了很多，你很激动地继续打胶，造成牛子不但没增加还缩短{format(reduce,'.2f')}cm了呢！"
          ])
    content[group][qq] = my_long
    readInfo('data/long.json',content)
  except KeyError:
    del group_hit_glue[group][qq]['time']
    result = random.choice([
      "你还没有牛子呢！不能打胶！",
      "无牛子，打胶不要的"
      ])
  finally:
    await niuzi_hit_glue.finish(Message(result),at_sender=True)

def pic2b64(pic: Image) -> str:
    """
    说明:
        PIL图片转base64
    参数:
        :param pic: 通过PIL打开的图片文件
    """
    buf = BytesIO()
    pic.save(buf, format="PNG")
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return "base64://" + base64_str
