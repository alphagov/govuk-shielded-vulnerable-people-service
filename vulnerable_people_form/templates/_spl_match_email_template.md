Dear {{first_name}} {{last_name}},

Your registration number is {{reference_number}}.

{% if not has_someone_to_shop %}

#If you need urgent help

Contact your local authority if you need urgent help: https://www.gov.uk/coronavirus-local-help

{% endif %}

#What happens next

{% if wants_supermarket_deliveries and wants_social_care %}

You should be able to start booking priority supermarket deliveries in the next 1 to 7 days, depending on the supermarket.

If you do not already have an account with a supermarket delivery service, set one up now. You can set up accounts with more than one supermarket if you're worried about not getting a delivery slot.

Someone from your local authority will contact you about your care needs within the next week.

{% endif %}

{% if wants_supermarket_deliveries and not wants_social_care %}

You should be able to start booking priority supermarket deliveries in the next 1 to 7 days, depending on the supermarket.

If you do not already have an account with a supermarket delivery service, set one up now. You can set up accounts with more than one supermarket if you're worried about not getting a delivery slot.

{% endif %}

{% if not wants_supermarket_deliveries and wants_social_care %}

Someone from your local authority will contact you about your care needs within the next week.

{% endif %}

{% if not wants_supermarket_deliveries and not wants_social_care %}

Based on what you told us, at the moment you do not help getting supplies or meeting your basic care needs.

{% endif %}

#If your personal details or support needs change

{% if has_set_up_account %}

Use your NHS login to update your personal details or support needs: https://www.gov.uk/coronavirus-shielding-support

{% endif %}

{% if not has_set_up_account %}

Go through the questions in the service again to update your personal details or support needs: https://www.gov.uk/coronavirus-shielding-support

{% endif %}

{% if has_someone_to_shop %}

Contact your local authority if you need support urgently and cannot rely on family, friends or neighbours: https://www.gov.uk/coronavirus-local-help

{% endif %}

There’s guidance on what you should do if you’re extremely vulnerable to coronavirus: https://www.gov.uk/coronavirus-extremely-vulnerable-guidance

Thanks,

National Shielding Service

-----

Do not reply to this email - it’s an automatic message from an unmonitored account.
