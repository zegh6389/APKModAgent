import os
import shutil
import re
import logging

import config

logger = logging.getLogger(__name__)

# --- SMALI CONTENT CONSTANTS ---

UPDATER_SMALI = """
.class public Lcom/myupdate/Updater;
.super Ljava/lang/Object;
.source "Updater.java"

# static fields
.field private static final CHECK_INTERVAL:J = 0x36ee80L
.field private static final PREFS_NAME:Ljava/lang/String; = "update_prefs"
.field private static final UPDATE_URL:Ljava/lang/String; = "https://your-website.com/update_config.json"
.field private static final KEY_LAST_CHECK:Ljava/lang/String; = "last_check_time"

# direct methods
.method public constructor <init>()V
    .locals 0

    .prologue
    .line 10
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


.method public static check(Landroid/content/Context;)V
    .locals 6
    .param p0, "context"    # Landroid/content/Context;

    .prologue
    # --- FIRST RUN GREETING CHECK ---
    const-string v2, "update_prefs"
    const/4 v3, 0x0
    invoke-virtual {p0, v2, v3}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;
    move-result-object v0

    const-string v2, "has_greeted"
    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z
    move-result v2

    if-nez v2, :cond_welcome

    # Show Welcome Dialog
    const-string v2, "https://t.me/YourTelegramChannel"
    invoke-static {p0, v2}, Lcom/myupdate/Updater;->showWelcomeDialog(Landroid/content/Context;Ljava/lang/String;)V

    # Save preference
    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;
    move-result-object v2
    const-string v3, "has_greeted"
    const/4 v4, 0x1
    invoke-interface {v2, v3, v4}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;
    move-result-object v2
    invoke-interface {v2}, Landroid/content/SharedPreferences$Editor;->apply()V

    :cond_welcome

    # --- UPDATE CHECK CHECK ---
    const-string v2, "last_check_time"

    const-wide/16 v4, 0x0

    invoke-interface {v0, v2, v4, v5}, Landroid/content/SharedPreferences;->getLong(Ljava/lang/String;J)J

    move-result-wide v2

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v4

    sub-long/2addr v2, v4

    invoke-static {v2, v3}, Ljava/lang/Math;->abs(J)J

    move-result-wide v2

    const-wide/32 v4, 0x36ee80

    cmp-long v2, v2, v4

    if-lez v2, :cond_0

    .line 24
    new-instance v1, Lcom/myupdate/FetchTask;

    invoke-direct {v1, p0}, Lcom/myupdate/FetchTask;-><init>(Landroid/content/Context;)V

    .line 25
    .local v1, "task":Lcom/myupdate/FetchTask;
    const/4 v2, 0x1

    new-array v2, v2, [Ljava/lang/String;

    const/4 v3, 0x0

    const-string v4, "https://your-website.com/update_config.json"

    aput-object v4, v2, v3

    invoke-virtual {v1, v2}, Lcom/myupdate/FetchTask;->execute([Ljava/lang/Object;)Landroid/os/AsyncTask;

    .line 26
    invoke-interface {v0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v2

    const-string v3, "last_check_time"

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v4

    invoke-interface {v2, v3, v4, v5}, Landroid/content/SharedPreferences$Editor;->putLong(Ljava/lang/String;J)Landroid/content/SharedPreferences$Editor;

    move-result-object v2

    invoke-interface {v2}, Landroid/content/SharedPreferences$Editor;->apply()V

    .line 28
    .end local v1    # "task":Lcom/myupdate/FetchTask;
    :cond_0
    return-void
.end method

.method public static showDialog(Landroid/content/Context;Ljava/lang/String;)V
    .locals 3
    .param p0, "context"    # Landroid/content/Context;
    .param p1, "url"    # Ljava/lang/String;

    .prologue
    .line 31
    new-instance v0, Landroid/app/AlertDialog$Builder;

    invoke-direct {v0, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    .line 32
    .local v0, "builder":Landroid/app/AlertDialog$Builder;
    const-string v1, "Update Available"

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    .line 33
    const-string v1, "A new version is available. check our telegram channel"

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    .line 34
    const/4 v1, 0x0

    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setCancelable(Z)Landroid/app/AlertDialog$Builder;

    .line 35
    const-string v1, "Update Now"

    new-instance v2, Lcom/myupdate/Updater$1;

    invoke-direct {v2, p1, p0}, Lcom/myupdate/Updater$1;-><init>(Ljava/lang/String;Landroid/content/Context;)V

    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    .line 44
    return-void
.end method

.method public static showWelcomeDialog(Landroid/content/Context;Ljava/lang/String;)V
    .locals 3
    .param p0, "context"    # Landroid/content/Context;
    .param p1, "url"    # Ljava/lang/String;

    .prologue
    new-instance v0, Landroid/app/AlertDialog$Builder;
    invoke-direct {v0, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    const-string v1, "Welcome!"
    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    const-string v1, "Thanks for using our Mod. Join us on Telegram for updates!"
    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setMessage(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    const/4 v1, 0x1
    invoke-virtual {v0, v1}, Landroid/app/AlertDialog$Builder;->setCancelable(Z)Landroid/app/AlertDialog$Builder;

    const-string v1, "Join Telegram"
    new-instance v2, Lcom/myupdate/Updater$1;
    invoke-direct {v2, p1, p0}, Lcom/myupdate/Updater$1;-><init>(Ljava/lang/String;Landroid/content/Context;)V
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setPositiveButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    const-string v1, "Close"
    const/4 v2, 0x0
    invoke-virtual {v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    invoke-virtual {v0}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;
    return-void
.end method
"""

UPDATER_INNER_SMALI = """
.class final Lcom/myupdate/Updater$1;
.super Ljava/lang/Object;
.source "Updater.java"

# interfaces
.implements Landroid/content/DialogInterface$OnClickListener;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/myupdate/Updater;->showDialog(Landroid/content/Context;Ljava/lang/String;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x8
    name = null
.end annotation


# instance fields
.field final synthetic val$context:Landroid/content/Context;
.field final synthetic val$url:Ljava/lang/String;


# direct methods
.method constructor <init>(Ljava/lang/String;Landroid/content/Context;)V
    .locals 0

    .prologue
    .line 35
    iput-object p1, p0, Lcom/myupdate/Updater$1;->val$url:Ljava/lang/String;

    iput-object p2, p0, Lcom/myupdate/Updater$1;->val$context:Landroid/content/Context;

    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method


# virtual methods
.method public onClick(Landroid/content/DialogInterface;I)V
    .locals 4
    .param p1, "dialog"    # Landroid/content/DialogInterface;
    .param p2, "which"    # I

    .prologue
    .line 38
    new-instance v0, Landroid/content/Intent;

    const-string v1, "android.intent.action.VIEW"

    iget-object v2, p0, Lcom/myupdate/Updater$1;->val$url:Ljava/lang/String;

    invoke-static {v2}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v2

    invoke-direct {v0, v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;Landroid/net/Uri;)V

    .line 39
    .local v0, "browserIntent":Landroid/content/Intent;
    iget-object v1, p0, Lcom/myupdate/Updater$1;->val$context:Landroid/content/Context;

    invoke-virtual {v1, v0}, Landroid/content/Context;->startActivity(Landroid/content/Intent;)V

    .line 40
    invoke-static {v3}, Ljava/lang/System;->exit(I)V
    return-void
.end method
"""

FETCHTASK_SMALI = """
.class public Lcom/myupdate/FetchTask;
.super Landroid/os/AsyncTask;
.source "FetchTask.java"


# annotations
.annotation system Ldalvik/annotation/Signature;
    value = {
        "Landroid/os/AsyncTask",
        "<",
        "Ljava/lang/String;",
        "Ljava/lang/Void;",
        "Ljava/lang/String;",
        ">;"
    }
.end annotation


# instance fields
.field private context:Landroid/content/Context;


# direct methods
.method public constructor <init>(Landroid/content/Context;)V
    .locals 0
    .param p1, "context"    # Landroid/content/Context;

    .prologue
    .line 18
    invoke-direct {p0}, Landroid/os/AsyncTask;-><init>()V

    .line 19
    iput-object p1, p0, Lcom/myupdate/FetchTask;->context:Landroid/content/Context;

    .line 20
    return-void
.end method


# virtual methods
.method protected bridge synthetic doInBackground([Ljava/lang/Object;)Ljava/lang/Object;
    .locals 1

    .prologue
    .line 14
    check-cast p1, [Ljava/lang/String;

    invoke-virtual {p0, p1}, Lcom/myupdate/FetchTask;->doInBackground([Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0

    return-object v0
.end method

.method protected varargs doInBackground([Ljava/lang/String;)Ljava/lang/String;
    .locals 7
    .param p1, "urls"    # [Ljava/lang/String;

    .prologue
    .line 24
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    .line 26
    .local v3, "result":Ljava/lang/StringBuilder;
    const/4 v5, 0x0

    :try_start_0
    aget-object v5, p1, v5

    new-instance v4, Ljava/net/URL;

    invoke-direct {v4, v5}, Ljava/net/URL;-><init>(Ljava/lang/String;)V

    .line 27
    .local v4, "url":Ljava/net/URL;
    invoke-virtual {v4}, Ljava/net/URL;->openConnection()Ljava/net/URLConnection;

    move-result-object v0

    check-cast v0, Ljava/net/HttpURLConnection;

    .line 28
    .local v0, "conn":Ljava/net/HttpURLConnection;
    const-string v5, "GET"

    invoke-virtual {v0, v5}, Ljava/net/HttpURLConnection;->setRequestMethod(Ljava/lang/String;)V

    .line 29
    new-instance v2, Ljava/io/BufferedReader;

    new-instance v5, Ljava/io/InputStreamReader;

    invoke-virtual {v0}, Ljava/net/HttpURLConnection;->getInputStream()Ljava/io/InputStream;

    move-result-object v6

    invoke-direct {v5, v6}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;)V

    invoke-direct {v2, v5}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;)V

    .line 31
    .local v2, "rd":Ljava/io/BufferedReader;
    :goto_0
    invoke-virtual {v2}, Ljava/io/BufferedReader;->readLine()Ljava/lang/String;

    move-result-object v1

    .local v1, "line":Ljava/lang/String;
    if-eqz v1, :cond_0

    .line 32
    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    goto :goto_0

    .line 35
    .end local v0    # "conn":Ljava/net/HttpURLConnection;
    .end local v1    # "line":Ljava/lang/String;
    .end local v2    # "rd":Ljava/io/BufferedReader;
    .end local v4    # "url":Ljava/net/URL;
    :catch_0
    move-exception v5

    .line 37
    :goto_1
    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    return-object v5

    .line 34
    .restart local v0    # "conn":Ljava/net/HttpURLConnection;
    .restart local v1    # "line":Ljava/lang/String;
    .restart local v2    # "rd":Ljava/io/BufferedReader;
    .restart local v4    # "url":Ljava/net/URL;
    :cond_0
    :try_start_1
    invoke-virtual {v2}, Ljava/io/BufferedReader;->close()V
    :try_end_1
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_0

    goto :goto_1
.end method

.method protected bridge synthetic onPostExecute(Ljava/lang/Object;)V
    .locals 0

    .prologue
    .line 14
    check-cast p1, Ljava/lang/String;

    invoke-virtual {p0, p1}, Lcom/myupdate/FetchTask;->onPostExecute(Ljava/lang/String;)V

    return-void
.end method

.method protected onPostExecute(Ljava/lang/String;)V
    .locals 6
    .param p1, "result"    # Ljava/lang/String;

    .prologue
    .line 43
    :try_start_0
    new-instance v1, Lorg/json/JSONObject;

    invoke-direct {v1, p1}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V

    .line 44
    .local v1, "json":Lorg/json/JSONObject;
    const-string v4, "versionCode"

    invoke-virtual {v1, v4}, Lorg/json/JSONObject;->getInt(Ljava/lang/String;)I

    move-result v3

    .line 45
    .local v3, "latestVersion":I
    const-string v4, "url"

    invoke-virtual {v1, v4}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2

    .line 47
    .local v2, "latestUrl":Ljava/lang/String;
    iget-object v4, p0, Lcom/myupdate/FetchTask;->context:Landroid/content/Context;

    invoke-virtual {v4}, Landroid/content/Context;->getPackageManager()Landroid/content/pm/PackageManager;

    move-result-object v4

    iget-object v5, p0, Lcom/myupdate/FetchTask;->context:Landroid/content/Context;

    invoke-virtual {v5}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v5

    const/4 v0, 0x0

    invoke-virtual {v4, v5, v0}, Landroid/content/pm/PackageManager;->getPackageInfo(Ljava/lang/String;I)Landroid/content/pm/PackageInfo;

    move-result-object v4

    iget v0, v4, Landroid/content/pm/PackageInfo;->versionCode:I

    .line 49
    .local v0, "currentVersion":I
    if-le v3, v0, :cond_0

    .line 50
    iget-object v4, p0, Lcom/myupdate/FetchTask;->context:Landroid/content/Context;

    invoke-static {v4, v2}, Lcom/myupdate/Updater;->showDialog(Landroid/content/Context;Ljava/lang/String;)V
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    .line 55
    .end local v0    # "currentVersion":I
    .end local v1    # "json":Lorg/json/JSONObject;
    .end local v2    # "latestUrl":Ljava/lang/String;
    .end local v3    # "latestVersion":I
    :cond_0
    :goto_0
    return-void

    .line 52
    :catch_0
    move-exception v4

    goto :goto_0
.end method
"""

def apply_mods(decode_dir, analysis=None):
    """
    Applies the specific SoundCloud mods:
    1. Removes GETMODPC files.
    2. Adds com.myupdate files.
    3. Injects code into LauncherActivity.

    Optionally accepts a precomputed `analysis` object from smali_scanner.analyze_smali_tree,
    which will be used in future iterations to choose better injection points.
    """
    # 1. REMOVAL (Clean Logic)
    # NOTE: We intentionally leave the GETMODPC classes and native libraries in place
    # to avoid ClassNotFoundException crashes in hosts that still reference them.
    # We only log their presence here so you can verify detection in the build logs.
    getmod_dir = os.path.join(decode_dir, "smali", "com", "GETMODPC")
    if os.path.exists(getmod_dir):
        logger.info(f"Detected legacy GETMODPC package at {getmod_dir}; leaving it intact")

    # Detect (but do not remove) any GETMODPC native libraries
    lib_dir = os.path.join(decode_dir, "lib")
    if os.path.exists(lib_dir):
        for root, dirs, files in os.walk(lib_dir):
            for file in files:
                if "GETMODPC" in file:
                    full_path = os.path.join(root, file)
                    logger.info(f"Detected legacy GETMODPC native library at {full_path}; leaving it intact")

    # 2. ADDITION (New Logic)
    # Create com/myupdate directory
    new_pkg_dir = os.path.join(decode_dir, "smali", "com", "myupdate")
    os.makedirs(new_pkg_dir, exist_ok=True)

    # Prepare templated Smali content using config values
    updater_smali = UPDATER_SMALI
    updater_smali = updater_smali.replace(
        "https://your-website.com/update_config.json",
        config.UPDATE_URL,
    )
    updater_smali = updater_smali.replace(
        "https://t.me/YourTelegramChannel",
        config.TELEGRAM_URL,
    )
    updater_smali = updater_smali.replace(
        "Welcome!",
        config.WELCOME_TITLE,
    )
    updater_smali = updater_smali.replace(
        "Thanks for using our Mod. Join us on Telegram for updates!",
        config.WELCOME_MESSAGE,
    )
    updater_smali = updater_smali.replace(
        "Update Available",
        config.UPDATE_DIALOG_TITLE,
    )
    updater_smali = updater_smali.replace(
        "A new version is available. check our telegram channel",
        config.UPDATE_DIALOG_MESSAGE,
    )

    fetchtask_smali = FETCHTASK_SMALI.replace(
        "https://your-website.com/update_config.json",
        config.UPDATE_URL,
    )

    # Write the new Smali files
    with open(os.path.join(new_pkg_dir, "Updater.smali"), "w") as f:
        f.write(updater_smali)
    with open(os.path.join(new_pkg_dir, "Updater$1.smali"), "w") as f:
        f.write(UPDATER_INNER_SMALI)
    with open(os.path.join(new_pkg_dir, "FetchTask.smali"), "w") as f:
        f.write(fetchtask_smali)

    # 3. INJECTION (Activity Hook)
    # For now we keep the original SoundCloud-specific heuristic. In the future we
    # can use `analysis.launcher_activity` and `analysis.getmodpc_call_sites` to
    # choose better injection points.
    launcher_path = None

    # Prefer manifest-based launcher resolution from the static analysis, if available.
    if analysis and getattr(analysis, "launcher_activity", None):
        candidate = getattr(analysis.launcher_activity, "smali_path", None)
        if candidate and os.path.exists(candidate):
            launcher_path = candidate
            logger.info(f"Using launcher activity from manifest analysis: {launcher_path}")
        else:
            logger.warning(
                "LauncherActivity from analysis has no valid smali path: %s",
                getattr(analysis.launcher_activity, "smali_path", None),
            )

    # Fallback to the legacy filesystem heuristic
    if not launcher_path:
        for root, dirs, files in os.walk(decode_dir):
            if "LauncherActivity.smali" in files:
                # Check if it's the right one (SoundCloud specific)
                if "soundcloud" in root:
                    launcher_path = os.path.join(root, "LauncherActivity.smali")
                    logger.info(f"Using launcher activity from filesystem scan: {launcher_path}")
                    break

    if not launcher_path:
        logger.error("LauncherActivity.smali not found!")
        return  # Cannot inject if not found

    logger.info(f"Injecting into {launcher_path}")

    with open(launcher_path, "r") as f:
        content = f.read()

    # --- FIX: REMOVE OLD GETMODPC CALLS ---
    # The previous mod likely injected a call like:
    #   invoke-static {p0}, Lcom/GETMODPC/A;->...(Landroid/content/Context;)V
    # We must remove it to prevent ClassNotFoundException
    if "Lcom/GETMODPC" in content:
        logger.info("Removing old GETMODPC references from LauncherActivity...")
        # Regex to remove lines with Lcom/GETMODPC
        # This removes the entire line containing the reference
        content = re.sub(r".*Lcom\\/GETMODPC.*", "", content)

    # Regex to find the onCreate method
    # .method ... onCreate(Landroid/os/Bundle;)V ... (code) ... return-void .end method
    #
    # We want to insert before 'return-void' in 'onCreate'
    # This is a simple heuristic; might need adjustment for complex methods
    pattern = r"(\\.method .*? onCreate\\(Landroid\\/os\\/Bundle;\\)V)(.*?)(\\n\\s+return-void)"

    match = re.search(pattern, content, re.DOTALL)

    if match and "Lcom/myupdate/Updater;->check" not in content:
        # Construct the replacement
        # Group 1: method header
        # Group 2: method body
        # Injection
        # Group 3: return-void
        injection = "\n    invoke-static {p0}, Lcom/myupdate/Updater;->check(Landroid/content/Context;)V"

        # We replace the found 'return-void' with 'injection + return-void'
        # But specifically ONLY inside the Match we found
        header = match.group(1)
        body = match.group(2)
        tail = match.group(3)

        new_block = f"{header}{body}{injection}{tail}"

        # Replace only the first occurrence (onCreate)
        new_content = content.replace(match.group(0), new_block)

        with open(launcher_path, "w") as f:
            f.write(new_content)

        logger.info("Injection successful.")
    else:
        logger.warning("Could not find onCreate or code already injected.")

