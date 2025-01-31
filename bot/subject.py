
from bot import bot
from data import UoM_blue, subjects, YEAR
from error import on_error,ValidationError
from paginator import Field
import requests
import discord
import re
from discord.ext import commands


subject_code_regex = r"^[a-zA-Z]{4}[0-9]{5}$"

def get_studentVIP_URL(code):
    return f"https://studentvip.com.au/unimelb/subjects/{code.lower()}"

def get_handbook_URL(code, year = YEAR):
    return f"https://handbook.unimelb.edu.au/{year}/subjects/{code.lower()}"

def add_availability_field(embed,subject):
    availability = subject['availability']
    avail_desc = []
    if len(availability) == 0:
        avail_desc = ["Not available in 2021"]
    else:
        for thing in availability:
            avail_desc.append(f"{thing['term']} - {thing['mode']}")
    avail_desc = "\n".join(avail_desc)
    embed.add_field(name = "Availability", value = avail_desc, inline = False)

def add_review_field(embed,subject):
    if (subject['rating'] == -1):
        subject_desc = "No ratings."
    else:
        subject_desc = f"Rated {subject['rating']} star(s) in {subject['review_count']} review(s)"
    embed.add_field(name = "StudentVIP rating:", value = subject_desc, inline = False)

def add_links_field(embed,subject):
    links = []
    if (subject['has_handbook_page']):
        links.append(f"[Handbook]({get_handbook_URL(subject['code'])})")
    if (subject['has_studentVIP_page']):
        links.append(f"[StudentVIP]({get_studentVIP_URL(subject['code'])})")
    links_desc = ""
    if (len(links) == 0):
        links_desc = "No links exist for this subject"
    else:
        links_desc = "\n".join(links)
    embed.add_field(name = "Links:", value = links_desc, inline = False)

# Precondition: subject is a dictionary entry from subjects.json
def get_subject_embed_detailed(subject):
    embed = discord.Embed(title=f"__{subject['title']} ({subject['code']})__", color=UoM_blue)
    if (not subject['has_handbook_page']):
        embed.description = f"Unfortunately {subject['code']} does not appear to have a handbook page," \
        " which means that little is known about the subject and it likely won't be offered to uni students in the future"
        return embed
    else:
        embed.description = f"{subject['level']} / Points: {subject['points']} / {subject['delivery']}"

        add_availability_field(embed,subject)
        
        if (subject['has_studentVIP_page']):
            add_review_field(embed,subject)
        
        add_links_field(embed,subject)   

    return embed

def subject_list_to_fields(subject_list):
    ret = []
    for subject in subject_list:
        title = f"{subject['code']}: {subject['title']}"
        desc = []
        if (subject["has_handbook_page"]):
            desc.append(f"[Handbook]({get_handbook_URL(subject['code'])})")
        if (subject['has_studentVIP_page']):
            desc.append(f"[StudentVIP]({get_studentVIP_URL(subject['code'])})")
        if (subject['points'] != 0):
            desc.append(f"Points: {subject['points']}")
        if (subject['delivery'] != ""):
            desc.append(f"{subject['delivery']}")
        
        desc = " / ".join(desc)
        ret.append(Field(title,desc))
    return ret

@bot.command()
async def subject(ctx, *args):
    if (len(args) != 1):
        raise ValidationError(f"Expecting exactly one argument. Usage is '{ctx.prefix}subject ABCD12345'. Case insensitive")

    subject_code = args[0].upper()

    if not re.match(subject_code_regex,subject_code):
        raise ValidationError(f"{subject_code} is an invalid subject code. Subject codes are of the form 'ABCD12345'. Case insensitive.")

    if subject_code.upper() not in subjects:
        raise ValidationError(f"Subject {subject_code} does not exist.")

    await ctx.send(embed = get_subject_embed_detailed(subject=subjects[subject_code]))        

@subject.error
async def subject_error(ctx, error):
    await on_error(ctx,error)
