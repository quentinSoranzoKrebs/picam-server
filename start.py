import os
import subprocess
import time
import signal
import sys

# Configuration
REPO_DIR = "./"  # Répertoire local du dépôt Git
BRANCH = "main"  # Branche à suivre
CHECK_INTERVAL = 60  # Intervalle entre les vérifications (en secondes)
PROCESS_COMMAND = ["python3", "main.py"]  # Commande pour lancer le processus principal

# Variables globales
process = None  # Référence au processus principal


def run_command(command, cwd=None):
    """Exécute une commande shell et retourne le résultat."""
    try:
        result = subprocess.run(
            command, cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return 1, "", str(e)


def is_update_available():
    """Vérifie si des mises à jour sont disponibles dans le dépôt Git."""
    code, stdout, stderr = run_command(["git", "fetch"], cwd=REPO_DIR)
    if code != 0:
        print(f"Erreur lors de 'git fetch': {stderr}")
        return False
    code, stdout, stderr = run_command(["git", "status", "-uno"], cwd=REPO_DIR)
    return "Votre branche est à jour" not in stdout


def apply_update():
    """Applique les mises à jour du dépôt Git."""
    code, stdout, stderr = run_command(["git", "pull", "origin", BRANCH], cwd=REPO_DIR)
    if code == 0:
        print("Mises à jour appliquées avec succès :")
        print(stdout)
        return True
    else:
        print(f"Erreur lors du 'git pull': {stderr}")
        return False


def restart_process():
    """Redémarre le processus principal."""
    global process
    if process is not None:
        print("Arrêt du processus en cours...")
        process.terminate()
        process.wait()
    print("Démarrage du nouveau processus...")
    process = subprocess.Popen(PROCESS_COMMAND, cwd=REPO_DIR)


def main():
    """Boucle principale pour vérifier et appliquer les mises à jour."""
    global process
    try:
        print("Démarrage du processus principal...")
        process = subprocess.Popen(PROCESS_COMMAND, cwd=REPO_DIR)

        while True:
            time.sleep(CHECK_INTERVAL)
            print("Vérification des mises à jour...")
            if is_update_available():
                print("Des mises à jour sont disponibles.")
                if apply_update():
                    print("Redémarrage du processus principal après mise à jour.")
                    restart_process()
            else:
                print("Pas de mises à jour disponibles.")
    except KeyboardInterrupt:
        print("Arrêt manuel détecté.")
    finally:
        if process is not None:
            print("Arrêt du processus principal...")
            process.terminate()
            process.wait()


if __name__ == "__main__":
    main()
