package main

/*
#include <stdlib.h>
*/
import "C"

import (
	"context"
	"fmt"
	"log"

	handlerService "github.com/xtls/xray-core/app/proxyman/command"
	routingService "github.com/xtls/xray-core/app/router/command"
	statsService "github.com/xtls/xray-core/app/stats/command"
	"github.com/xtls/xray-core/common/protocol"
	"github.com/xtls/xray-core/common/serial"
	"github.com/xtls/xray-core/proxy/vless"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
)

type XrayController struct {
	HsClient handlerService.HandlerServiceClient
	SsClient statsService.StatsServiceClient
	RsClient routingService.RoutingServiceClient
	CmdConn  *grpc.ClientConn
}

type Client struct {
	grpcClient  *grpc.ClientConn
	isConnected bool
	HsClient    handlerService.HandlerServiceClient
}

type BaseConfig struct {
	APIAddress string
	APIPort    uint16
}

func (xrayCtl *XrayController) Init(cfg *BaseConfig) error {
	address := fmt.Sprintf("%s:%d", cfg.APIAddress, cfg.APIPort)

	conn, err := grpc.Dial(
		address,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithBlock(), // Ожидание соединения
	)
	if err != nil {
		return fmt.Errorf("gRPC connection failed: %v", err)
	}

	xrayCtl.CmdConn = conn
	xrayCtl.HsClient = handlerService.NewHandlerServiceClient(conn)
	xrayCtl.SsClient = statsService.NewStatsServiceClient(conn)
	xrayCtl.RsClient = routingService.NewRoutingServiceClient(conn)

	log.Printf("gRPC clients initialized (connected to %s)", address)
	return nil
}

var globalClient *Client

//export InitClient
func InitClient(address *C.char) {

	apiAddress := C.GoString(address)
	conn, err := grpc.Dial(
		apiAddress,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
	)
	if err != nil {
		log.Fatalf("Failed to create gRPC connection: %v", err)
	}

	globalClient = &Client{
		grpcClient: conn,
		HsClient:   handlerService.NewHandlerServiceClient(conn),
	}

	log.Printf("gRPC client initialized")
}

//export getUsers
func getUsers() *C.char {
	if globalClient == nil || globalClient.HsClient == nil {
		log.Println("Client is not initialized")
		return C.CString("error: client not initialized")
	}

	ctx := context.Background()
	tag := "vless_tls"

	userList, err := globalClient.HsClient.GetInboundUsers(ctx, &handlerService.GetInboundUserRequest{
		Tag: tag,
	})
	if err != nil {
		log.Printf("Failed to get users: %v", err)
		return C.CString("error: failed to get users")
	}

	// Возвращаем как строку (protobuf сообщение форматируется)
	return C.CString(fmt.Sprintf("%v", userList))
}

//export addUser
func addUser(email *C.char, id *C.char) *C.char {
	if globalClient == nil || globalClient.HsClient == nil {
		log.Println("Client is not initialized")
		return C.CString("error: client not initialized")
	}

	ctx := context.Background()

	// Преобразуем C строку в Go строку
	emailStr := C.GoString(email)
	idStr := C.GoString(id)

	inboundTag := "vless_tls"

	resp, err := globalClient.HsClient.AlterInbound(ctx, &handlerService.AlterInboundRequest{
		Tag: inboundTag,
		Operation: serial.ToTypedMessage(
			&handlerService.AddUserOperation{
				User: &protocol.User{
					Email: emailStr,
					Account: serial.ToTypedMessage(&vless.Account{
						Id:   idStr,
						Flow: "xtls-rprx-vision",
					}),
				},
			}),
	})

	if err != nil {
		log.Printf("AlterInbound failed: %v", err)
		return C.CString(fmt.Sprintf("error: %v", err))
	}

	log.Println("User added successfully")

	return C.CString(fmt.Sprintf("%v", resp))

}

func main() {

	getUsers()
}
