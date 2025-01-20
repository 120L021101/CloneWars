#!/bin/sh
#SBATCH --account=Education-EEMCS-Courses-CS4570
#SBATCH --partition=gpu-a100
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=5
#SBATCH --mem-per-cpu=8000
#SBATCH --time=1-00:00:00\
#SBATCH --gpus-per-task 1
python /scratch/zujizhou/team-14/train/util.py >/scratch/zujizhou/team-14/train/log 2>/scratch/zujizhou/team-14/train/err