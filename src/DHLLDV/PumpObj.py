"""
PumpObj: Object to simulate a pump and driver

Added by R. Ramsdell 03 September, 2021
"""

# def generate_pump_curve(MaximumFlow As Double, MaxIndex As Integer, CarrierLiquidDensity As Double, MixtureDensity As Double, APump As Double, CPump As Double, SolidsEfficiency As Double, MaxPower As Double, Limited As String, Revolutions As Double, DesignFlow As Double, MaximumPumpEfficiency As Double, ModeIndex As Integer)
#   Dim Storage() As Variant, StorageRange As String, Index As Integer, Flow As Double, PumpPower As Double, PumpPressure As Double, FirstTime1 As Boolean, FirstTime2 As Boolean, ActualRevolutions As Double
#   Dim PumpEfficiency(501) As Double, MaxFlow As Double, X As Double, MinEfficiency As Double, MaxEfficiency As Double, PumpMaxTorque As Double, PumpOmega As Double, Alpha1 As Double, Alpha2 As Double
#
#   PumpOmega = 2 * Pi * Revolutions / 60
#   PumpMaxTorque = MaxPower / PumpOmega
#   ActualRevolutions = Revolutions
#   MinEfficiency = MinimumPumpEfficiency
#   MaxEfficiency = MaximumPumpEfficiency
#   MaxFlow = (-APump / CPump) ^ 0.5
#   For Index = 1 To MaxIndex + 1
#     Flow = (Index - 1) / MaxIndex * MaximumFlow
#     If Flow <= DesignFlow Then
#       X = Flow / (2 * DesignFlow)
#     Else
#       X = 0.5 + 0.5 * (Flow - DesignFlow) / (MaxFlow - DesignFlow)
#     End If
#     If X > 1 Then X = 1
#     PumpEfficiency(Index) = (MaxEfficiency - MinEfficiency) * (4 * X - 4 * X ^ 2) ^ 0.5 + MinEfficiency
#   Next Index
#
#   StorageRange = "A4:CZ504"
#   Sheets("Pumps").Select
#   Storage() = Range(StorageRange)
#   FirstTime1 = True
#   FirstTime2 = True
#   For Index = 1 To MaxIndex + 1
#     'Flow
#     Flow = (Index - 1) / MaxIndex * MaximumFlow
#     Storage(Index, 1 + (ModeIndex - 1) * 6) = Flow
#
#     'Carrier liquid curve
#     PumpPressure = CarrierLiquidDensity * (APump + CPump * Flow ^ 2)
#     PumpPower = PumpPressure * Flow / PumpEfficiency(Index)
#     If (PumpPower > MaxPower) And FirstTime1 Then
#       Alpha1 = PumpPressure / Revolutions ^ 2 / PumpEfficiency(Index)
#       FirstTime1 = False
#     End If
#     If (Limited = "TORQUE") And Not FirstTime1 Then
#       'If PumpPressure > Alpha1 * (2 * Pi / 60 * PumpMaxTorque / (Alpha1 * Flow)) ^ 2 * PumpEfficiency(Index) Then
#         PumpPressure = Alpha1 * (2 * Pi / 60 * PumpMaxTorque / (Alpha1 * Flow)) ^ 2 * PumpEfficiency(Index)
#       'End If
#     ElseIf Limited = "POWER" And (PumpPressure * Flow > MaxPower * PumpEfficiency(Index)) Then
#       PumpPressure = MaxPower * PumpEfficiency(Index) / Flow
#     Else
#       PumpPressure = PumpPressure
#     End If
#     Storage(Index, 2 + (ModeIndex - 1) * 6) = PumpPressure
#     PumpPower = PumpPressure * Flow / PumpEfficiency(Index)
#     If Flow > MaxFlow Then PumpPower = 0
#     Storage(Index, 3 + (ModeIndex - 1) * 6) = PumpPower
#
#     'Mixture curve
#     PumpPressure = MixtureDensity * (APump + CPump * Flow ^ 2) * SolidsEfficiency
#     PumpPower = PumpPressure * Flow / PumpEfficiency(Index) / SolidsEfficiency
#     If (PumpPower > MaxPower) And FirstTime2 Then
#       Alpha2 = PumpPressure / Revolutions ^ 2 / SolidsEfficiency / PumpEfficiency(Index)
#       FirstTime2 = False
#     End If
#     If (Limited = "TORQUE") And Not FirstTime2 Then
#       'If PumpPressure > Alpha2 * (2 * Pi / 60 * PumpMaxTorque / (Alpha2 * Flow)) ^ 2 * PumpEfficiency(Index) * SolidsEfficiency Then
#         ActualRevolutions = (2 * Pi / 60 * PumpMaxTorque / (Alpha2 * Flow))
#         PumpPressure = Alpha2 * (2 * Pi / 60 * PumpMaxTorque / (Alpha2 * Flow)) ^ 2 * PumpEfficiency(Index) * SolidsEfficiency
#       'End If
#     ElseIf Limited = "POWER" And (PumpPressure * Flow > MaxPower * PumpEfficiency(Index) * SolidsEfficiency) Then
#       PumpPressure = MaxPower * PumpEfficiency(Index) * SolidsEfficiency / Flow
#     Else
#       PumpPressure = PumpPressure
#     End If
#     Storage(Index, 4 + (ModeIndex - 1) * 6) = PumpPressure
#     PumpPower = PumpPressure * Flow / PumpEfficiency(Index) / SolidsEfficiency
#     If Flow > MaxFlow Then PumpPower = 0
#     Storage(Index, 5 + (ModeIndex - 1) * 6) = PumpPower
#
#   Next Index
#   Range(Stor