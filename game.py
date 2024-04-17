from collections import defaultdict
from dataclasses import dataclass
from math import ceil
from typing import List


# FIXME: Rename all "actions" to "activites"


player_stats = {
    "shadowy": 150,
    "watchful": 161,
    "dangerous": 118,
    "persuasive": 150,
    "respectable": 8,
    "dreaded": 5,
    "bizarre": 7,
}


class GameTree:
    global player_stats
    global LIST_OF_ACTIVITIES

    def __init__(self):
        self._input_index = defaultdict(list)
        self._output_index = defaultdict(list)

        self._constructIndex()
        # print(self._input_index)
        # print(self._output_index)

    def _constructIndex(self):
        # Need to disambiguate same-name actions
        seen_activity_names = set()
        for activity in LIST_OF_ACTIVITIES:
            activity_name = activity.description
            if activity_name in seen_activity_names:
                append_int = 1
                while f'{activity_name} ({append_int})' in seen_activity_names:
                    append_int += 1
                # Update action itself to have the disambiguated name
                activity_name = f'{activity_name} ({append_int})'
                activity.description = activity_name
            seen_activity_names.add(activity_name)
            
            for inp in activity.inputs:
                self._input_index[inp].append(activity)
            for out in activity.outputs:
                self._output_index[out].append(activity)


@dataclass
class Activity:
    description: str
    actions: float
    inputs: dict[str, float]
    outputs: dict[str, float]

    def __hash__(self):
        return hash(self.description)

    def __repr__(self):
        return f'Activity({self.description})'


def broad(quality, difficulty):
    return max(0, min(1, 0.6 * quality / difficulty))

def narrow(quality, difficulty, increment=.1):
    if quality <= difficulty:
        return min(increment, .5 - increment * (difficulty - quality))
    else:
        return max(1, .5 + increment * (quality - difficulty))



def computeHeistActions(player_stats, heist_security) -> float:
    # Upper bound average assuming you have one card slot
    # Assume there are enough favors
    if heist_security == "shuttered":
        return 1 + 5 / ((1 + 0 + 2 + 0.4 + 2 + 1)/6)
    elif heist_security == "triple-bolted":
        tds_yield_with_favors = (
            2 if player_stats['shadowy'] >= 100
            else 0
        )
        return 1 + 5 / ((1 + 2 + 0 + 1 + 2 + 2 + 0.4 + tds_yield_with_favors + 1)/9)


def levelToCP(level):
    # level 0 -> 1 = 1 cp
    # level 1 -> 2 = 2 cp (total 3)
    # level 2 -> 3 = 3 cp (total 6)
    # So formula is n(n+1)/2
    return level * (level + 1) // 2


LIST_OF_ACTIVITIES = [
    # Activity(
    #     description="heist - balustraded house in elderwick",
    #     actions=computeHeistActions(player_stats, "triple-bolted"),
    #     inputs={
    #         "casing": levelToCP(8),
    #         "favours: criminals": 5,
    #     },
    #     outputs={
    #         "shadowy": 20,
    #         "ostentatious diamond": 10,
    #         "surface-silk scrap": 25,
    #         "magnificent diamond": 1,
    #         "puzzle-damask scrap": 1,
    #     },
    # ),
    # Activity(
    #     description="heist - balustraded house in elderwick",
    #     actions=computeHeistActions(player_stats, "triple-bolted"),
    #     inputs={
    #         "casing": levelToCP(8),
    #         "favours: criminals": 5,
    #     },
    #     outputs={
    #         "shadowy": 20,
    #         "ostentatious diamond": 10,
    #         "surface-silk scrap": 25,
    #         "favour in high places": 1,
    #         "puzzle-damask scrap": 1,
    #     },
    # ),
    Activity(
        description="purchase some assistance with casing...",
        actions=1,
        inputs={
            "talkative rattus faber": 3,
        },
        outputs={
            "casing": 9,
        },
    ),
    Activity(
        description="bazaar purchase - talkative rattus faber",
        actions=0,
        inputs={
            "echoes": 0.8
        },
        outputs={
            "talkative rattus faber": 1,
        },
    ),
    Activity(
        description="bazaar sell",
        actions=0,
        inputs={
            "puzzle-damask scrap": 1,
        },
        outputs={
            "echoes": 12.5,
        },
    ),
    Activity(
        description="bazaar sell",
        actions=0,
        inputs={
            "ostentatious diamond": 1,
        },
        outputs={
            "echoes": 0.5,
        },
    ),
    Activity(
        description="bazaar sell",
        actions=0,
        inputs={
            "surface-silk scrap": 1,
        },
        outputs={
            "echoes": 0.1,
        },
    ),
    Activity(
        description="arrange for a personal recommendation",
        actions=1,
        inputs={
            "stolen kiss": 6,
            "compromising document": 30,
            "intriguing snippet": 150,
        },
        outputs={
            "personal recommendation": 1
        },
    ),
    Activity(
        description="upconvert - compromising document -> stolen kiss",
        actions=1,
        inputs={
            "compromising document": 50,
        },
        outputs={
            "stolen kiss": 10,
            "first city coin": 1.2,
            "making waves": 6,
        },
    ),
    Activity(
        description="upconvert - intriguing snippet -> compromising document",
        actions=1,
        inputs={
            "intriguing snippet": 250,
        },
        outputs={
            "compromising document": 105,
        },
    ),
    Activity(
        description="a trade in reputations - ms winthrop's purifying soap",
        actions=15,
        inputs={},
        outputs={
            "intriguing snippet": 125,
        },
    ),
    # Activity(
    #     description="see if the big rat can become intoxicated",
    #     actions=1,
    #     inputs={
    #         "bottle of greyfields 1882": 50,
    #     },
    #     outputs={
    #         "mystery of the elder continent": 0.7,
    #         "intriguing snippet": 7,
    #     },
    # ),
    Activity(
        description="bazaar purchase - bottle of greyfields 1882",
        actions=0,
        inputs={
            "echoes": 0.04,
        },
        outputs={
            "bottle of greyfields 1882": 1,
        },
    ),
    Activity(
        description="solicit favours in high places",
        actions=1,
        inputs={
            "cryptic clue": 200,
            "an identity uncovered!": 1,
            "secluded address": 1,
            "scrap of incendiary gossip": 1,
            "inkling of identity": 25,
        },
        outputs={
            "favour in high places": 1,
        },
    ),
    Activity(
        description="attend courtly functions",
        actions=1,
        inputs={},
        outputs={
            "whispered hint": 90*0.8,
        },
    ),
    Activity(
        description="bazaar purchase - drop of prisoner's honey",
        actions=0,
        inputs={
            "echoes": 0.04,
        },
        outputs={
            "drop of prisoner's honey": 1,
        },
    ),
    Activity(
        description="supply wine in exchange for prisoner's honey",
        actions=1,
        inputs={
            "bottle of greyfields 1879": 50,
        },
        outputs={
            "drop of prisoner's honey": 40,
            "making waves": 1,
        },
    ),
    Activity(
        description="bazaar purchase - bottle of greyfields 1879",
        actions=0,
        inputs={
            "echoes": 0.02,
        },
        outputs={
            "bottle of greyfields 1879": 1,
        },
    ),
    Activity(
        description="doing the decent thing",
        actions=1,
        inputs={},
        outputs={
            # TODO: Automate away this calculation
            # 63% success (7% rare success)
            # 30% failure
            "drop of prisoner's honey": .63*50 + .07*(100-11)/2,
            "stolen kiss": 0.07,
            "scandal": 0.6,
        },
    ),
    # Activity(
    #     description="heist - mansion of an unsympathetic landlord",
    #     # TODO: Fix to be well-guarded
    #     actions=computeHeistActions(player_stats, "triple-bolted"),
    #     inputs={
    #         "casing": levelToCP(8),
    #     },
    #     outputs={
    #         "shadowy": 70,
    #         "fistful of surface currency": 340,
    #         "piece of rostygold": 1200,
    #         "brilliant soul": (6+38)//2,
    #     },
    # ),
    Activity(
        description="bazaar sell",
        actions=0,
        inputs={
            "piece of rostygold": 1,
        },
        outputs={
            "echoes": 0.01,
        },
    ),
    Activity(
        description="bazaar sell",
        actions=0,
        inputs={
            "fistful of surface currency": 1,
        },
        outputs={
            "echoes": 0.03,
        },
    ),
    Activity(
        description="thefts of a particular character - bazaar permit",
        actions=1,
        # ~52% success
        inputs={
            "casing": .52*32 + .48*51,
        },
        outputs={
            "bazaar permit": 1,
        },
    ),
    Activity(
        description="heist - mr baseborn's papers",
        # TODO: Fix to be well-guarded
        actions=computeHeistActions(player_stats, "triple-bolted") + 2,
        inputs={
            "casing": levelToCP(8),
        },
        outputs={
            "shadowy": 20,
            "cryptic clue": 100,
            "bazaar permit": 2,
        },
    ),
    Activity(
        description="bazaar sell",
        actions=0,
        inputs={
            "cryptic clue": 1
        },
        outputs={
            "echoes": 0.02,
        },
    ),
    # Activity(
    #     description="obtain a permit from the bazaar",
    #     actions=1,
    #     inputs={
    #         "vision of the surface": 10,
    #         "romantic notion": 100,
    #     },
    #     outputs={
    #         "bazaar permit": 1,
    #     },
    # ),
    # Activity(
    #     description="take biscuits in the parlor",
    #     actions=1,
    #     inputs={},
    #     outputs={
    #         "romantic notion": 7
    #     },
    # ),
    Activity(
        description="compile a book of hidden bodies",
        actions=1,
        inputs={
            "an identity uncovered!": 6,
            "scrap of incendiary gossip": 30,
            "inkling of identity": 300,
        },
        outputs={
            "book of hidden bodies": 1,
        },
    ),
    Activity(
        description="spread some currency around",
        actions=1,
        inputs={
            "piece of rostygold": 100,
        },
        outputs={
            "scrap of incendiary gossip": 2,
        },
    ),
    Activity(
        description="attend: and be erudite",
        actions=1,
        inputs={},
        outputs={
            "inkling of identity": 7,
        },
    ),
    Activity(
        description="hire strong-backed labour",
        actions=1,
        inputs={
            "echoes": 3.5,
        },
        outputs={
            "strong-backed labour": 1,
        },
    ),
    Activity(
        description="recruit clay man labour",
        actions=1,
        inputs={
            "moon-pearl": 50,
            "piece of rostygold": 50,
            "compromising document": 4,
            "an identity uncovered!": 1,
        },
        outputs={
            "strong-backed labour": 2,
        },
    ),
    Activity(
        description="underclay - send unfinished to teach fourth city history",
        # https://fallenlondon.wiki/wiki/Underclay_(Guide)
        # Taken when shadowy = 114, persuasive = 123
        # Actions are:
        # Calcified -> extract confessions (59.04%)
        # Unfinished -> invent fabricated histories (77.73%)
        # Need to get 1 of each, so 1/0.5904 + 1/0.7773 = 2.98 actions avg
        # 25/18.32
        actions=2.98 + 3,
        inputs={},
        outputs={
            "an identity uncovered!": 2,
        },
    ),
    Activity(
        description="bazaar purchase - moon-pearl",
        actions=0,
        inputs={
            "echoes": 0.03,
        },
        outputs={
            "moon-pearl": 1,
        },
    ),
    Activity(
        description="bazaar purchase - piece of rostygold",
        actions=0,
        inputs={
            "echoes": 0.03,
        },
        outputs={
            "piece of rostygold": 1,
        },
    ),
    Activity(
        # TODO: Split this into two activities? Requires solver handling of spending all
        description="underclay - send unfinished to spite",
        actions=(
            2 # enter exit
            + 2 / broad(player_stats['shadowy'], 125) # assume 30 stone confession action
        ),
        inputs={},
        outputs={
            "strong-backed labour": 3,
            "shard of glim": ((ceil(2 / broad(player_stats['shadowy'], 125)) * 30) % 50) * 10,
        },
    ),
    Activity(
        description="bazaar sell",
        actions=0,
        inputs={
            "shard of glim": 1
        },
        outputs={
            "echoes": 0.01,
        },
    ),
]
