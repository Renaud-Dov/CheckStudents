class French:
    changeLanguage = "La langue du bot est maintenant en **français**"
    unknownCommand = "Commande inconnue : Commandes envoyées en message privé"
    classMsg = ["**Classe :**", "**__Résumé appel__**"]
    sendAbsents = ["**Par :**", "**Serveur :**", "**Channel :**", ["Voir message", "Lien"]]
    commands = [
        "**Voici la liste des commandes que vous pouvez utiliser\n Par défaut, le préfixe du bot est .Check.**",
        ["call", "Lance l'appel (*remplacer par la classe correspondante*)"],
        ["add ***@role1 @role2 ...***", "Ajoute les privilèges à un rôle ou plus"],
        ["remove (ou rm) ***@role1 @role2 ...    ***", "Retire les privilèges à un ou plusieurs rôles"],
        ["language en|fr|de", "Change le language du bot dans les langues suivantes : English, French or German"],
        ["list (ou roles)", "Retourne les rôles ayant un privilège"],
        ["reset", "Réinitialise le bot"],
        ["prefix", "Change le préfix du bot"],
        ["sysMessages (ou sys)", "Active ou désactive les messages système du bot"],
        ["DeactivateMP", "Active ou désactive les messages privés"],
        ["settings", "Retourne la valeurs des paramètres actuels"],
        ["Pour plus d'informations", "[Cliquer ici](https://github.com/Renaud-Dov/CheckStudents)"]
    ]
    NoStudents = "⚠ **Aucun élève présent** ⚠"
    EndCall = [
        "**Elèves présents :**\n",
        "**Elèves non présents :\n**",
        "\n ✅ **Tous les élèves sont présents** ✅"
    ]
    FinishCall = " a fini l'appel des"
    cancelCall = "⚠ **Appel annulé** ⚠"
    NoRightEnd = "**Vous n'avez pas les droits pour fermer l'appel !**"
    unknownEmoji = "**Emoji inconnu.\nLes élèves doivent cliquer sur ✅ pour se notifier présent.**"
    cantNotify = "Vous ne pouvez pas vous notifier présent"
    notTeacher = "**Vous n'êtes pas professeur ! Vous ne pouvez démarrer l'appel.**"
    NoPrivileges = "**Vous n'avez pas les privilèges!**\n*Utiliser `admin list` pour voir les rôles d'admin*"
    zeroPrivileges = "**Il n'y a aucun rôle ayant les privilèges! Pour en rajouter : `.Check add @role1 @role2, etc...`**"
    removeAdmin = "Admin retiré"
    notAdmin = "n'est pas admin"
    newAdmin = ["Nouvel Admin :", "rôle dejà ajouté", "rôle non valide"]
    rolenotValid = "Rôle non valide : Pour plus d'information : `.Check help`"
    startcall = ["Début de l'appel",
                 "**Elèves : Cliquez sur ✅ pour vous notifier présent\nProfesseur : Cliquez sur 🆗 pour valider l'appel ou 🛑 pour l'annuler**",
                 "Classe appelée :", "Besoin d'aide ? Utilisez la commande help"]

    newPrefix = "Nouveau préfix : "
