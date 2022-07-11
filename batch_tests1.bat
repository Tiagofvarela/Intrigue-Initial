::::Montecarlo vs Random::::

::Random::
@REM python3.9 .\play_game.py 10 montecarlo -m1 random random random
@REM python3.9 .\play_game.py 10 random montecarlo -m1 random random
@REM python3.9 .\play_game.py 10 random random montecarlo -m1 random
@REM python3.9 .\play_game.py 10 random random random montecarlo -m1

::Honest::
python3.9 .\play_game.py 10 montecarlo -m1 honest honest honest
python3.9 .\play_game.py 10 honest montecarlo -m1 honest honest
python3.9 .\play_game.py 10 honest honest montecarlo -m1 honest
python3.9 .\play_game.py 10 honest honest honest montecarlo -m1

::Greedy::
python3.9 .\play_game.py 10 montecarlo -m1 greedy greedy greedy
python3.9 .\play_game.py 10 greedy montecarlo -m1 greedy greedy
python3.9 .\play_game.py 10 greedy greedy montecarlo -m1 greedy
python3.9 .\play_game.py 10 greedy greedy greedy montecarlo -m1

::TitforTat::
python3.9 .\play_game.py 10 montecarlo -m1 titfortat titfortat titfortat
python3.9 .\play_game.py 10 titfortat montecarlo -m1 titfortat titfortat
python3.9 .\play_game.py 10 titfortat titfortat montecarlo -m1 titfortat
python3.9 .\play_game.py 10 titfortat titfortat titfortat montecarlo -m1

::Everyone::
python3.9 .\play_game.py 10 montecarlo -m1 titfortat greedy honest
python3.9 .\play_game.py 10 titfortat montecarlo -m1 greedy honest
python3.9 .\play_game.py 10 titfortat greedy montecarlo -m1 honest
python3.9 .\play_game.py 10 titfortat greedy honest montecarlo -m1

