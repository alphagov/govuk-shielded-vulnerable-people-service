Dear {{first_name}} {{last_name}},

Your registration number is {{reference_number}}.

#What happens next

{% if not has_someone_to_shop and wants_supermarket_deliveries and wants_social_care %}

You should be able to start booking priority supermarket deliveries in the next 1 to 7 days, depending on the supermarket.

If you do not already have an account with a supermarket delivery service, set one up now. You can set up accounts with more than one supermarket if you're worried about not getting a delivery slot.

If people in your area are told to start shielding, your local authority will contact you to talk about any additional needs you have.

{% endif %}

{% if not has_someone_to_shop and wants_supermarket_deliveries and not wants_social_care %}

You should be able to start booking priority supermarket deliveries in the next 1 to 7 days, depending on the supermarket.

If you do not already have an account with a supermarket delivery service, set one up now. You can set up accounts with more than one supermarket if you're worried about not getting a delivery slot.

{% endif %}

{% if not has_someone_to_shop and not wants_supermarket_deliveries and wants_social_care %}

If people in your area are told to start shielding, your local authority will contact you to talk about what support you need in order to shield.

In the meantime, contact your local authority if you need urgent help and cannot rely on friends, family or neighbours: https://www.gov.uk/coronavirus-local-help

You won’t get the help you need if you do not contact them.

{% endif %}

{% if not has_someone_to_shop and not wants_supermarket_deliveries and not wants_social_care %}

Based on what you told us, you do not need support at the moment.

{% endif %}

{% if has_someone_to_shop and wants_social_care %}

If people in your area are told to start shielding, your local authority will contact you to talk about what support you need in order to shield.

In the meantime, contact your local authority if you need urgent help and cannot rely on friends, family or neighbours: https://www.gov.uk/coronavirus-local-help

You won’t get the help you need if you do not contact them.

{% endif %}

{% if has_someone_to_shop and not wants_social_care %}

Based on what you told us, you do not need support at the moment.

{% endif %}

#If your personal details or support needs change

{% if has_set_up_account %}

Use your NHS login to update your personal details or support needs: https://www.gov.uk/coronavirus-shielding-support

{% endif %}

{% if not has_set_up_account %}

Go through the questions in the service again to update your personal details or support needs: https://www.gov.uk/coronavirus-shielding-support

{% endif %}

{% if ((not has_someone_to_shop and not wants_supermarket_deliveries and wants_social_care) or (has_someone_to_shop and wants_social_care)) %}

Contact your local authority right away if you need urgent help and cannot rely on family, friends or neighbours: https://www.gov.uk/coronavirus-local-help

{% endif %}

Make sure you’re up to date with the guidance on what you can and cannot do if you’re clinically extremely vulnerable to coronavirus: https://www.gov.uk/coronavirus-extremely-vulnerable-guidance

Regards,

Coronavirus support team
