echo -e "\n##########################\n# Sorting imports alphabetically\n##########################"
isort .

echo -e "\n##########################\n# Running black\n##########################"
black takethetools

#echo -e "\n##########################\n# mypy on takethetools\n##########################"
#mypy takethetools

echo -e "\n##########################\n# pylint on takethetools\n##########################"
pylint takethetools/*