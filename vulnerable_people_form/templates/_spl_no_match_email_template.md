Dear {{first_name}} {{last_name}},

Your registration number is {{reference_number}}.

{% if told_to_shield == 1 %}

#Make sure you've given us the correct personal details

You'll only be able to get the support you need if you've given us the correct personal details. If you think you might have made a mistake, go through the questions again: https://www.gov.uk/coronavirus-shielding-support

Contact your local authority if you need help using the service: https://www.gov.uk/coronavirus-local-help

#What happens next

You do not need to do anything else if you've been told to shield by the NHS or your doctor and they've put you on the NHS list of people who should be shielding.

We’ll check your details, then contact you to confirm whether you’re eligible for support. You will not start getting support until we’ve confirmed that you’re eligible. This can take up to 2 weeks.

{% endif %}

{% if told_to_shield == 2 or told_to_shield ==  3 %}

#Contact your GP

Contact your GP or hospital clinician as soon as possible so they can put you on the NHS list of people who should be shielding. You may not get the support you need if you do not contact them.

#Make sure you've given us the correct personal details

You'll only be able to get the support you need if you've given us the correct personal details. If you think you might have made a mistake, go through the questions again: https://www.gov.uk/coronavirus-shielding-support

Contact your local authority if you need help using the service: https://www.gov.uk/coronavirus-local-help

#What happens next

We’ll check your details, then contact you to confirm whether you’re eligible for support. This can take up to 2 weeks from when your GP or hospital clinician puts you on the NHS list of people who should be shielding.

{% endif %}

#If you need urgent help

Contact your local authority if you need support urgently and cannot rely on family, friends or neighbours: https://www.gov.uk/coronavirus-local-help

There’s guidance on what you should do if you’re extremely vulnerable to coronavirus: https://www.gov.uk/coronavirus-extremely-vulnerable-guidance

Thanks,

National Shielding Service

-----

Do not reply to this email - it’s an automatic message from an unmonitored account.
