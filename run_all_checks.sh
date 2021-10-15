echo -e "\n##########################\n# Sorting imports alphabetically\n##########################"
isort .

echo -e "\n##########################\n# Running black\n##########################"
black src

echo -e "\n##########################\n# mypy on src\n##########################"
MYPYPATH=src mypy src

echo -e "\n##########################\n# pylint on takethetools\n##########################"
pylint src/*