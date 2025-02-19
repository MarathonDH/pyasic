# ------------------------------------------------------------------------------
#  Copyright 2022 Upstream Data Inc                                            -
#                                                                              -
#  Licensed under the Apache License, Version 2.0 (the "License");             -
#  you may not use this file except in compliance with the License.            -
#  You may obtain a copy of the License at                                     -
#                                                                              -
#      http://www.apache.org/licenses/LICENSE-2.0                              -
#                                                                              -
#  Unless required by applicable law or agreed to in writing, software         -
#  distributed under the License is distributed on an "AS IS" BASIS,           -
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    -
#  See the License for the specific language governing permissions and         -
#  limitations under the License.                                              -
# ------------------------------------------------------------------------------
from dataclasses import dataclass, field
from typing import Union

from pyasic.config.base import MinerConfigOption, MinerConfigValue


@dataclass
class FanModeNormal(MinerConfigValue):
    mode: str = field(init=False, default="normal")

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]) -> "FanModeNormal":
        return cls()

    def as_am_modern(self) -> dict:
        return {"bitmain-fan-ctrl": False, "bitmain-fan-pwn": "100"}

    def as_bosminer(self) -> dict:
        return {"temp_control": {"mode": "auto"}}


@dataclass
class FanModeManual(MinerConfigValue):
    mode: str = field(init=False, default="manual")
    speed: int = 100
    minimum_fans: int = 1

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]) -> "FanModeManual":
        cls_conf = {}
        if dict_conf.get("speed") is not None:
            cls_conf["speed"] = dict_conf["speed"]
        if dict_conf.get("minimum_fans") is not None:
            cls_conf["minimum_fans"] = dict_conf["minimum_fans"]
        return cls(**cls_conf)

    @classmethod
    def from_bosminer(cls, toml_fan_conf: dict) -> "FanModeManual":
        cls_conf = {}
        if toml_fan_conf.get("min_fans") is not None:
            cls_conf["minimum_fans"] = toml_fan_conf["min_fans"]
        if toml_fan_conf.get("speed") is not None:
            cls_conf["speed"] = toml_fan_conf["speed"]
        return cls(**cls_conf)

    def as_am_modern(self) -> dict:
        return {"bitmain-fan-ctrl": True, "bitmain-fan-pwn": str(self.speed)}

    def as_bosminer(self) -> dict:
        return {
            "temp_control": {"mode": "manual"},
            "fan_control": {"min_fans": self.minimum_fans, "speed": self.speed},
        }


@dataclass
class FanModeImmersion(MinerConfigValue):
    mode: str = field(init=False, default="immersion")

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]) -> "FanModeImmersion":
        return cls()

    def as_am_modern(self) -> dict:
        return {"bitmain-fan-ctrl": True, "bitmain-fan-pwn": "0"}

    def as_bosminer(self) -> dict:
        return {"temp_control": {"mode": "disabled"}}


class FanModeConfig(MinerConfigOption):
    normal = FanModeNormal
    manual = FanModeManual
    immersion = FanModeImmersion

    @classmethod
    def default(cls):
        return cls.normal()

    @classmethod
    def from_dict(cls, dict_conf: Union[dict, None]):
        if dict_conf is None:
            return cls.default()

        mode = dict_conf.get("mode")
        if mode is None:
            return cls.default()

        clsattr = getattr(cls, mode)
        if clsattr is not None:
            return clsattr().from_dict(dict_conf)

    @classmethod
    def from_am_modern(cls, web_conf: dict):
        if web_conf.get("bitmain-fan-ctrl") is not None:
            fan_manual = web_conf["bitmain-fan-ctrl"]
            if fan_manual:
                return cls.manual(speed=web_conf["bitmain-fan-pwm"])
            else:
                return cls.normal()
        else:
            return cls.default()

    @classmethod
    def from_epic(cls, web_conf: dict):
        try:
            fan_mode = web_conf["Fans"]["Fan Mode"]
            if fan_mode.get("Manual") is not None:
                return cls.manual(speed=fan_mode.get("Manual"))
            else:
                return cls.normal()
        except KeyError:
            return cls.default()

    @classmethod
    def from_bosminer(cls, toml_conf: dict):
        if toml_conf.get("temp_control") is None:
            return cls.default()
        if toml_conf["temp_control"].get("mode") is None:
            return cls.default()

        mode = toml_conf["temp_control"]["mode"]
        if mode == "auto":
            return cls.normal()
        elif mode == "manual":
            if toml_conf.get("fan_control"):
                return cls.manual().from_bosminer(toml_conf["fan_control"])
            return cls.manual()
        elif mode == "disabled":
            return cls.immersion()
