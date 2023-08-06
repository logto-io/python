from .models.oidc import IdTokenClaims, AccessTokenClaims
from .OidcCore import OidcCore

class TestOidcCore:
  def test_generateState(self):
    assert len(OidcCore.generateState()) == 43

  def test_generateCodeVerifier(self):
    assert len(OidcCore.generateCodeVerifier()) == 43

  def test_generateCodeChallenge(self):
    codeVerifier = '12345678901234567890123456789012345678901234567890'
    assert OidcCore.generateCodeChallenge(codeVerifier) == '9Y__uhKapn7GO_ElcaQpd8C3hdOyqTzAU4VXyR2iEV0'

  def test_decodeIdToken(self):
    idToken = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJpc3MiOiJodHRwczovL2xvZ3RvLmFwcCIsImF1ZCI6ImZvbyIsImV4cCI6MTYxNjQ0NjQwMCwiaWF0IjoxNjE2NDQ2MzAwLCJzdWIiOiJ1c2VyMSIsIm5hbWUiOiJKb2huIFdpY2siLCJ1c2VybmFtZSI6ImpvaG4iLCJlbWFpbCI6ImpvaG5Ad2ljay5jb20iLCJlbWFpbF92ZXJpZmllZCI6dHJ1ZX0.12345678901234567890123456789012345678901234567890'
    assert OidcCore.decodeIdToken(idToken) == IdTokenClaims(
      iss='https://logto.app',
      aud='foo',
      exp=1616446400,
      iat=1616446300,
      sub='user1',
      name='John Wick',
      username='john',
      email='john@wick.com',
      email_verified=True,
    )

  def test_decodeAccessTokenWithResourceAndClientId(self):
    accessToken = 'eyJhbGciOiJSUzI1NiIsImtpZCI6IjEifQ.eyJpc3MiOiJodHRwczovL2xvZ3RvLmFwcCIsImF1ZCI6Imh0dHBzOi8vbG9ndG8uYXBwL2FwaSIsImV4cCI6MTYxNjQ0NjQwMCwiaWF0IjoxNjE2NDQ2MzAwLCJzdWIiOiJ1c2VyMSIsInNjb3BlIjoiYWRtaW4gdXNlciIsImNsaWVudF9pZCI6InNhcXJlMW9xYmtwajZ6aHE4NWhvMCJ9.12345678901234567890123456789012345678901234567890'
    assert OidcCore.decodeAccessToken(accessToken) == AccessTokenClaims(
      iss='https://logto.app',
      aud='https://logto.app/api',
      exp=1616446400,
      iat=1616446300,
      sub='user1',
      scope='admin user',
      client_id='saqre1oqbkpj6zhq85ho0',
    )
