Dear {{first_name}} {{last_name}},

Your registration number is {{reference_number}}.

{% if not has_someone_to_shop %}

#If you need urgent help

Contact your local authority if you need urgent help: www.gov.uk/coronavirus-local-help.

{% endif %}

#What happens next

{% if wants_supermarket_deliveries and wants_social_care %}

You should now be able to start booking priority deliveries with supermarkets.

If you do not already have an account with a supermarket delivery service, set one up now. You can set up accounts with more than one supermarket if you're worried about not getting a delivery slot.

Someone from your local authority will contact you about your care needs within the next week.

{% endif %}

{% if wants_supermarket_deliveries and not wants_social_care %}

You should now be able to get priority access to supermarket deliveries.

If you do not already have an account with a supermarket delivery service, set one up now. You can set up accounts with more than one supermarket if you're worried about not getting a delivery slot.

{% endif %}

{% if not wants_supermarket_deliveries and wants_social_care %}

Someone from your local authority will contact you about your care needs within the next week.

{% endif %}

{% if not wants_supermarket_deliveries and not wants_social_care %}

You said that you do not want priority supermarket deliveries or help with your care needs.

{% endif %}

#If your personal details or support needs change

Use the service again to update your personal details or support needs: www.gov.uk/coronavirus-extremely-vulnerable

{% if has_someone_to_shop %}

Contact your local authority if you need support urgently and cannot rely on family, friends or neighbours: www.gov.uk/coronavirus-local-help

{% endif %}

There’s guidance on what you should do if you’re extremely vulnerable to coronavirus: www.gov.uk/coronavirus-extremely-vulnerable-guidance

Regards,

National Shielding Service
