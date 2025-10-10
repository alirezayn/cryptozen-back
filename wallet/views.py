from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.request import Request
from .serializers import UserWalletSerializer, WalletTransactionSerializer,WithdrawHistorySerializer
from .service import WalletService


class WalletBalanceView(generics.GenericAPIView):
    serializer_class = UserWalletSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request:Request):
        balance = WalletService.get_balance(request.user)
        return Response({"balance": balance})
    

class WalletDepositView(generics.GenericAPIView):
    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request: Request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            result = WalletService.deposit(request.user, serializer.validated_data["amount"])
            status_code = status.HTTP_201_CREATED if result["success"] else status.HTTP_400_BAD_REQUEST
            return Response(result, status=status_code)
        return Response({"success": False, "message": "Invalid data", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

class WalletWithdrawView(generics.GenericAPIView):
    serializer_class = WalletTransactionSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request:Request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            wallet = WalletService.withdraw(request.user, serializer.validated_data["amount"])
            return Response(wallet, status=status.HTTP_200_OK)
        return Response({"success": False, "message": "Invalid data", "data": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

    

class WithdrawHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        withdraw_history_qs = WalletService.get_withdraw_requests(request.user)
        serializer = WithdrawHistorySerializer(withdraw_history_qs, many=True)
        return Response({
            "success": True,
            "data": serializer.data,
            "message": "Withdraw history fetched successfully"
        }, status=status.HTTP_200_OK)