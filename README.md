![Version](https://img.shields.io/badge/version-1.00-green)
![Github](https://img.shields.io/badge/license-GNU3-orange)
# CheckStudents
Pour rajouter ce bot à ce serveur, cliquez sur le lien suivant : https://discord.com/oauth2/authorize?client_id=760157065997320192&permissions=8&scope=bot
## Fonctionnement


Pour voir les élèves présents à un cours, un professeur (ou toute autre utilisateur ayant un role autorisé voir PARTIE ~)

>Pour faire l'appel d'une classe, il suffit de d'envoyer `.Check appel @Classe` (remplacer `@classe` par le role correspondant)
<img src="img/img1.png" alt="Capture d'écran d'une recherche">

>Des émojis vont apparaitre en dessous de votre message, les élèves faisant partie de la `@classe` pourront cliquer sur le ✅ pour notifier leur présence.
Le professeur, ou n'importe quelle personne ayant les droits pourra finir l'appel en cliquant sur 🆗.
<img src="img/img2.png" alt="Capture d'écran d'une recherche">

>Note : Les utilisateurs ne peuvent notifier leur présence que si ils font partie du groupe (les élèves extérieurs ne seront pas comptabilisés.)
>De même, quelqu'un qui n'a pas les privilèges ne peut fermet l'appel
<img src="img/img3.png" alt="Capture d'écran d'une recherche">


Une fois l'appel terminé, le bit retournera la liste des élèves présents (sortira les élèves non présent dans une MAJ).
<img src="img/img4.png" alt="Capture d'écran d'une recherche">

## Initialisation

Pour initialiser le bot, vous devez écrire `.Check init @roleBot @admin` -> @roleBot correspond au role du bot CheckStudents et @admin le rôle de privilège.
<img src="img/img5.png" alt="Capture d'écran d'une recherche">
​
5

## Ajouter/Supprimer des privilèges à un rôle

Seul un utilisateur ayant les privilèges peut rajouter/supprimer des rôles.

* Ajouter : `.Check addRole @role1 @role2,...` 
* Supprimer : `.Check rmRole @role1 @role2,...`
>Note : Vous pouvez rajouter/supprimer autant de role que vous vouler à la fois.


Icons made by <a href="http://www.freepik.com/" title="Freepik">Freepik</a> from <a href="https://www.flaticon.com/" title="Flaticon"> www.flaticon.com</a>
