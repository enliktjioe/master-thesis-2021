# Normal SSH

ssh enlik@rocket.hpc.ut.ee


# SSH Tunneling jupyter notebook in UT HPC server

- ssh -L 8888:localhost:8888 enlik@rocket.hpc.ut.ee
- run `conda activate th` (activate conda env 'th' with python 3.8)
- run `jupyter notebook`
- open web browser and type localhost:8888


# Enable Table of Content in Jupyter Notebook

- Use `jupyter_contrib_nbextensions` from [source](https://github.com/ipython-contrib/jupyter_contrib_nbextensions)
- To be able export HTML with toc, run `conda install "nbconvert=5.6.1"` [source](https://stackoverflow.com/questions/65376052/how-to-solve-error-with-downloading-jupyter-notebook-as-html-with-toc)


# Export UT HPC Server specification

- run `lshw -html > server_specs.html` [source](https://ourcodeworld.com/articles/read/768/how-to-check-system-specifications-in-ubuntu-server-16-04-with-the-cli)

# Trouble Shooting LDA Mallet Path on Windows 10

- https://stackoverflow.com/questions/24126187/error-when-implementing-gensim-ldamallet