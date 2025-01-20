#!/bin/sh
#
#SBATCH --job-name="nmouman-file-dedup"
#SBATCH --partition=compute
#SBATCH --time=01:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=8
#SBATCH --mem-per-cpu=10G
#SBATCH --account=Education-EEMCS-Courses-CS4570

export OMP_NUM_THREADS=$SLURM_CPUS_PER_TASK

module load 2023r1
module load openmpi
module load python/3.9.8
module load py-pip
python -m pip install --upgrade --user datasets

python util.py