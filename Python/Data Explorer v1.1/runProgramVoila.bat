@echo off
start voila RunFile.ipynb && (
    echo Successful Command
) || (
    echo voila may not be installed. Try running DBInteractorSetup
)
