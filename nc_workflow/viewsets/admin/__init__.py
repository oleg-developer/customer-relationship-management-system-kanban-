from nc_auth.permissions import IsCompanyOwner, IsAuthenticated

PERMISSION_CLASSES = (IsAuthenticated, IsCompanyOwner,)
