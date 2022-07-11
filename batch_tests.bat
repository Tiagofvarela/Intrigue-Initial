::::Montecarlo vs Random::::

::DefaultTime, DefaultC, DefaultEval::
python3.9 .\play_game.py 10 montecarlo -t random random random
python3.9 .\play_game.py 10 random montecarlo -t random random
python3.9 .\play_game.py 10 random random montecarlo -t random
python3.9 .\play_game.py 10 random random random montecarlo -t

::DefaultTime, HighC, DefaultEval::
python3.9 .\play_game.py 10 montecarlo -t -1.7 random random random
python3.9 .\play_game.py 10 random montecarlo -t -1.7 random random
python3.9 .\play_game.py 10 random random montecarlo -t -1.7 random
python3.9 .\play_game.py 10 random random random montecarlo -t -1.7

::DefaultTime, HighC, GreedyEval::
python3.9 .\play_game.py 10 montecarlo -t -1.7 -g random random random
python3.9 .\play_game.py 10 random montecarlo -t -1.7 -g random random
python3.9 .\play_game.py 10 random random montecarlo -t -1.7 -g random
python3.9 .\play_game.py 10 random random random montecarlo -t -1.7 -g

::DefaultTime, LowC, DefaultEval::
python3.9 .\play_game.py 10 montecarlo -t -1.1 random random random
python3.9 .\play_game.py 10 random montecarlo -t -1.1 random random
python3.9 .\play_game.py 10 random random montecarlo -t -1.1 random
python3.9 .\play_game.py 10 random random random montecarlo -t -1.1

::DefaultTime, LowC, GreedyEval::
python3.9 .\play_game.py 10 montecarlo -t -1.1 -g random random random
python3.9 .\play_game.py 10 random montecarlo -t -1.1 -g random random
python3.9 .\play_game.py 10 random random montecarlo -t -1.1 -g random
python3.9 .\play_game.py 10 random random random montecarlo -t -1.1 -g

::DefaultTime, DefaultC, GreedyEval::
python3.9 .\play_game.py 10 montecarlo -t -g random random random
python3.9 .\play_game.py 10 random montecarlo -t -g random random
python3.9 .\play_game.py 10 random random montecarlo -t -g random
python3.9 .\play_game.py 10 random random random montecarlo -t -g

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::HighTime, DefaultC, DefaultEval::
python3.9 .\play_game.py 10 montecarlo -t -40 random random random
python3.9 .\play_game.py 10 random montecarlo -t -40 random random
python3.9 .\play_game.py 10 random random montecarlo -t -40 random
python3.9 .\play_game.py 10 random random random montecarlo -t -40

::HighTime, HighC, DefaultEval::
python3.9 .\play_game.py 10 montecarlo -t -40 -1.7 random random random
python3.9 .\play_game.py 10 random montecarlo -t -40 -1.7 random random
python3.9 .\play_game.py 10 random random montecarlo -t -40 -1.7 random
python3.9 .\play_game.py 10 random random random montecarlo -t -40 -1.7

::HighTime, HighC, GreedyEval::
python3.9 .\play_game.py 10 montecarlo -t -40 -1.7 -g random random random
python3.9 .\play_game.py 10 random montecarlo -t -40 -1.7 -g random random
python3.9 .\play_game.py 10 random random montecarlo -t -40 -1.7 -g random
python3.9 .\play_game.py 10 random random random montecarlo -t -40 -1.7 -g

::HighTime, LowC, DefaultEval::
python3.9 .\play_game.py 10 montecarlo -t -40 -1.1 random random random
python3.9 .\play_game.py 10 random montecarlo -t -40 -1.1 random random
python3.9 .\play_game.py 10 random random montecarlo -t -40 -1.1 random
python3.9 .\play_game.py 10 random random random montecarlo -t -40 -1.1

::HighTime, LowC, GreedyEval::
python3.9 .\play_game.py 10 montecarlo -t -40 -1.1 -g random random random
python3.9 .\play_game.py 10 random montecarlo -t -40 -1.1 -g random random
python3.9 .\play_game.py 10 random random montecarlo -t -40 -1.1 -g random
python3.9 .\play_game.py 10 random random random montecarlo -t -40 -1.1 -g

::HighTime, DefaultC, GreedyEval::
python3.9 .\play_game.py 10 montecarlo -t -40 -g random random random
python3.9 .\play_game.py 10 random montecarlo -t -40 -g random random
python3.9 .\play_game.py 10 random random montecarlo -t -40 -g random
python3.9 .\play_game.py 10 random random random montecarlo -t -40 -g

:::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::

::LowTime, DefaultC, DefaultEval::
python3.9 .\play_game.py 10 montecarlo -t -10 random random random
python3.9 .\play_game.py 10 random montecarlo -t -10 random random
python3.9 .\play_game.py 10 random random montecarlo -t -10 random
python3.9 .\play_game.py 10 random random random montecarlo -t -10

::LowTime, HighC, DefaultEval::
python3.9 .\play_game.py 10 montecarlo -t -10 -1.7 random random random
python3.9 .\play_game.py 10 random montecarlo -t -10 -1.7 random random
python3.9 .\play_game.py 10 random random montecarlo -t -10 -1.7 random
python3.9 .\play_game.py 10 random random random montecarlo -t -10 -1.7

::LowTime, HighC, GreedyEval::
python3.9 .\play_game.py 10 montecarlo -t -10 -1.7 -g random random random
python3.9 .\play_game.py 10 random montecarlo -t -10 -1.7 -g random random
python3.9 .\play_game.py 10 random random montecarlo -t -10 -1.7 -g random
python3.9 .\play_game.py 10 random random random montecarlo -t -10 -1.7 -g

::LowTime, LowC, DefaultEval::
python3.9 .\play_game.py 10 montecarlo -t -10 -1.1 random random random
python3.9 .\play_game.py 10 random montecarlo -t -10 -1.1 random random
python3.9 .\play_game.py 10 random random montecarlo -t -10 -1.1 random
python3.9 .\play_game.py 10 random random random montecarlo -t -10 -1.1

::LowTime, LowC, GreedyEval::
python3.9 .\play_game.py 10 montecarlo -t -10 -1.1 -g random random random
python3.9 .\play_game.py 10 random montecarlo -t -10 -1.1 -g random random
python3.9 .\play_game.py 10 random random montecarlo -t -10 -1.1 -g random
python3.9 .\play_game.py 10 random random random montecarlo -t -10 -1.1 -g

::LowTime, DefaultC, GreedyEval::
python3.9 .\play_game.py 10 montecarlo -t -10 -g random random random
python3.9 .\play_game.py 10 random montecarlo -t -10 -g random random
python3.9 .\play_game.py 10 random random montecarlo -t -10 -g random
python3.9 .\play_game.py 10 random random random montecarlo -t -10 -g